from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         # No file uploaded
#         return redirect(request.url)
    
#     file = request.files['file']
    
#     if file.filename == '':
#         # No file selected
#         return redirect(request.url)
    
#     file.save('uploads/' + file.filename)
    
#     # Additional processing or rendering logic
    
#     return 'File uploaded successfully!'


@app.route('/result', methods=['POST'])
def count_words():
    count = 0;
    if request.method == 'POST':
        count = 98;
        if 'file' not in request.files:
            # No file uploaded
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            # No file selected
            return redirect(request.url)
        
        file.save('uploads/' + file.filename)
        
    # Additional processing or rendering logic

    return render_template('result.html', number_of_words=count)

if __name__ == '__main__':    
    app.run();