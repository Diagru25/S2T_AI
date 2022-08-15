import soundfile as sf
import torch
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC, pipeline
import soundfile as sf
import torchaudio
import kenlm # pip3 install https://github.com/kpu/kenlm/archive/master.zip
from pyctcdecode import Alphabet, BeamSearchDecoderCTC, LanguageModel
# Improvements: 
# - gpu / cpu flag
# - convert non 16 khz sample rates
# - inference time log

# cache_dir = './cache/'

# lm_file_auth = cache_dir + 'vi_lm_4grams.bin'

class Wave2Vec2Inference():
    def __init__(self,model_name, hotwords=[]):
        self.processor = Wav2Vec2Processor.from_pretrained(model_name,cache_dir=None, local_files_only=True)
        self.model = Wav2Vec2ForCTC.from_pretrained(model_name,cache_dir=None, local_files_only=True)
        self.hotwords = hotwords
        # cache_dir = './cache/'
        self.lm_file = './cache/vi_lm_4grams.bin'

    def get_decoder_ngram_model(self, processor, ngram_lm_path):
        vocab_dict = self.processor.tokenizer.get_vocab()
        sort_vocab = sorted((value, key) for (key, value) in vocab_dict.items())
        vocab = [x[1] for x in sort_vocab][:-2]
        vocab_list = vocab
        # convert ctc blank character representation
        vocab_list[self.processor.tokenizer.pad_token_id] = ""
        # replace special characters
        vocab_list[self.processor.tokenizer.unk_token_id] = ""
        # vocab_list[tokenizer.bos_token_id] = ""
        # vocab_list[tokenizer.eos_token_id] = ""
        # convert space character representation
        vocab_list[self.processor.tokenizer.word_delimiter_token_id] = " "
        # specify ctc blank char index, since conventially it is the last entry of the logit matrix
        alphabet = Alphabet.build_alphabet(vocab_list, ctc_token_idx=self.processor.tokenizer.pad_token_id)
        lm_model = kenlm.Model(ngram_lm_path)
        decoder = BeamSearchDecoderCTC(alphabet, language_model=LanguageModel(lm_model))
        return decoder

    def buffer_to_text(self,audio_buffer):
        ngram_lm_model = self.get_decoder_ngram_model(self.processor, self.lm_file)
        if(len(audio_buffer)==0):
            return ""

        # inputs = self.processor(torch.tensor(audio_buffer), sampling_rate=16_000, return_tensors="pt", padding=True)
        input_values = self.processor(torch.tensor(audio_buffer), return_tensors="pt", sampling_rate=16000)["input_values"]
        logits = self.model(input_values).logits[0]
        beam_search_output = ngram_lm_model.decode(logits.cpu().detach().numpy(), beam_width=500)

        # with torch.no_grad():
        #     result = self.model(inputs.input_values)
        #     logits = result.logits
        #
        # if hasattr(self.processor, 'decoder'):
        #     transcription = \
        #         self.processor.decode(logits[0].cpu().numpy(),
        #                               hotwords=self.hotwords,
        #                               #hotword_weight=self.hotword_weight,
        #                            )
        #     transcription = transcription.text
        # else:
        #     predicted_ids = torch.argmax(logits, dim=-1)
        #     transcription = self.processor.batch_decode(predicted_ids)[0]

        return beam_search_output

    def file_to_text(self,filename):
        audio_input, samplerate = sf.read(filename)
        # assert samplerate == 16000
        return self.buffer_to_text(audio_input)
    
if __name__ == "__main__":
    print("Model test")
    asr = Wave2Vec2Inference("./model_best")
    text = asr.file_to_text("audio.wav")
    print(text)