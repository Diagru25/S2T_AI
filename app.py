
import os
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

from run import get_transcription
import os
import warnings
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, Wav2Vec2Tokenizer
from run import get_transcription, get_decoder_ngram_model
import pandas

UPLOAD_FOLDER = os.getcwd()
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#declare path
warnings.filterwarnings("ignore")
dir_path = os.path.dirname(os.path.realpath(__file__))
model_path = os.path.join(dir_path, 'model_best')
cache_dir = './cache/'

lm_file = cache_dir + 'vi_lm_4grams.bin'

#load model
model = Wav2Vec2ForCTC.from_pretrained(model_path, cache_dir=None, local_files_only=True)
processor = Wav2Vec2Processor.from_pretrained(model_path, cache_dir=None, local_files_only=True)

ngram_lm_model = get_decoder_ngram_model(processor.tokenizer, lm_file)


#function
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def search_object(text = ""):
    icon_list_result = []
    location_list_result = []

    excel_data_df = pandas.read_excel('khqs.xlsx', usecols=['MaKHQS', 'TuKhoa'])
    icon_list = excel_data_df.to_dict(orient='records')
    for icon in icon_list:
        keyword_list = icon['TuKhoa'].split(',')
        for c in keyword_list:
            keyword = c.strip().lower()
            if(keyword in text):
                icon_list_result.append(str(icon['MaKHQS']))
    
    
    location_list = []

    return icon_list_result, location_list_result

def responseData(value):
    icon_ids, locations = search_object(value)
    data = {'text': value, 
            'icon_ids': icon_ids, 
            'locations': locations
            }
    return jsonify(data)

@app.route("/", methods=["GET"])
def welcome():
    return "Speech2Text API"


@app.route("/transcription", methods=["POST"])
def run():
  if request.method == 'POST':
        print(request.files)
    # check if the post request has the file part
        if 'file' not in request.files:
            return responseData('')
        file = request.files['file']
        
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return responseData('')
        if file and allowed_file(file.filename):
            file_ext = file.filename.split('.')[1]
            filename = "audio." + file_ext
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            #transcription
            text = get_transcription(processor, model, ngram_lm_model, filename)
            return responseData(text)

if __name__ == "__main__":
    app.run(debug=True, port=5001, host="0.0.0.0")
