from flask import Flask, render_template, request, redirect
import os
import services.DIP

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def count_words():
    number_of_words = -1;
    if request.method == 'POST':
        if 'file' not in request.files:
            # No file uploaded
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            # No file selected
            return redirect(request.url)
        
        file.save('uploads/' + file.filename)

    # Additional processing or rendering logic
    path = 'uploads' + '\\' + file.filename; 
    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

    number_of_words = services.DIP.countWord(image_path);

    return render_template('result.html', number_of_words=number_of_words)


if __name__ == '__main__':    
    app.run();