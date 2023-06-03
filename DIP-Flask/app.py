from flask import Flask, render_template, request, redirect, send_file
import os
import services.wordCounter
import services.scoreExtractor

app = Flask(__name__)


@app.route('/download')
def download_file():
    root_path = (os.path.dirname(os.path.abspath(__file__)));
    dssv_scores_path= os.path.join(root_path, "static", "files", "dssv_scores.xlsx");

    return send_file(dssv_scores_path, as_attachment=True)

@app.route('/', methods=['GET', 'POST'])
def count_words():
    fileName = "No file here";
    fileSize = "0 KB";
    number_of_words = 0;

    if request.method == 'GET':
        return render_template('index.html', activeTabRender="tab1", fileName=fileName, fileSize=fileSize, number_of_words=number_of_words)
   
    if request.method == 'POST':
        if 'file-image' not in request.files:
            # No file uploaded
            return redirect('/', code=302)
        
        fileImage = request.files['file-image']
        
        if fileImage.filename == '':
            # No file selected
            return redirect('/', code=302)
       
        fileImage_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'images', fileImage.filename)
        fileImage.save(fileImage_path)
        
        activeTab = request.form.get('activeTab')
        if activeTab == "tab1":
            if 'file-dssv' not in request.files:
                return redirect('/', code=302)
            
            fileDSSV = request.files['file-dssv']
            if  fileDSSV.filename == '':
                # No file selected
                return redirect('/', code=302)
            
            fileDSSV_path = os.path.join('uploads', 'files', fileDSSV.filename)
            fileDSSV.save(fileDSSV_path)
            
            fileName, fileSize, filePath = services.scoreExtractor.extractScore(fileImage_path, fileDSSV_path);
            
            return render_template('index.html', activeTabRender=activeTab, number_of_words=number_of_words, fileName=fileName, fileSize=fileSize)  
        if activeTab == "tab2":
            number_of_words = services.wordCounter.countWord(fileImage_path);
            return render_template('index.html', activeTabRender=activeTab, number_of_words=number_of_words, fileName=fileName, fileSize=fileSize)

        return render_template('index.html',activeTabRender="tab1", fileName=fileName, fileSize=fileSize, number_of_words=number_of_words)
    
    
if __name__ == '__main__':    
    app.run();