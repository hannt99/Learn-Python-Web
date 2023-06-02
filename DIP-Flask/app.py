from flask import Flask, render_template, request, redirect
import os
import services.DIP

app = Flask(__name__)
   

@app.route('/', methods=['GET', 'POST'])
def count_words():
    number_of_words = 0;

    if request.method == 'GET':
        print('GET method')
        return render_template('index.html', number_of_words=number_of_words)
   
    if request.method == 'POST':
        print('POST method')
        print(f'request.files:{request.files}')
        if 'file-image' not in request.files:
            # No file uploaded
            print('No file uploaded')
            print(f'request.files:{request.files}')
            return redirect('/', code=302)

        file = request.files['file-image']
        
        if file.filename == '':
            # No file selected
            print('No file selected')
            print(f'file.filename:{file.filename}')
            return redirect('/', code=302)
        
        file.save('uploads/' + file.filename)

    # Additional processing or rendering logic
    path = 'uploads' + '\\' + file.filename; 
    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

    # if request.form. == "tab1"
    #     dssv_scores = services.scoreExtractor.extractScore(image_path);
    #     return render_template('index.html', number_of_words=number_of_words)
    # else:  # request.form. == "tab2"
    #     number_of_words = services.wordCounter.countWord(image_path);
    #     return render_template('index.html', number_of_words=number_of_words)


if __name__ == '__main__':    
    app.run();