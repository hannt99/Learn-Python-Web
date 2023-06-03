import os
import numpy as np
import cv2
import operator
import pytesseract
import pandas as pd
import math

def pre_process_image(img, skip_dilate=False):
    """
        Uses a blurring function, adaptive thresholding and dilation to expose the main features of an image.
    """
    # Gaussian blur with a kernel size (width, height) of 9
    # Note that kernel sizes must be positive, odd and the kernel must be square.
    proc = cv2.GaussianBlur(src=img, ksize=(9, 9), sigmaX=0, sigmaY=0)

    # Adaptive threshold using 11 nearest neighbor pixels
    proc = cv2.adaptiveThreshold(proc, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    # Necessary to dilate the image, otherwise will look like erosion instead.
    if not skip_dilate:
        # Dilate the image to increase the size of the grid lines.
        kernel = np.array([
                            [0., 1., 0.], 
                            [1., 1., 1.], 
                            [0., 1., 0.]
                            ], np.uint8)
        proc = cv2.dilate(src=proc, kernel=kernel, iterations=1)

    return proc

def find_corners_of_largest_polygon(img):
    """
        Finds the 4 extreme corners of the largest contour in the image.
    """
    opencv_version = cv2.__version__.split('.')[0]
    if opencv_version == '3':
        _, contours, h = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # Find contours
    else:
        contours, h = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # Find contours
        contours = sorted(contours, key=cv2.contourArea, reverse=True) # Sort by area, descending
        polygon = contours[0] # Largest image

    # Use of `operator.itemgetter` with `max` and `min` allows us to get the index of the point
    # Each point is an array of 1 coordinate, hence the [0] getter, then [0] or [1] used to get x and y respectively.
    
    # Top-left point has smallest (x + y) value
    top_left, _ = min(enumerate([pt[0][0] + pt[0][1] for pt in polygon]), key=operator.itemgetter(1))
    # Top-right point has largest (x - y) value
    top_right, _ = max(enumerate([pt[0][0] - pt[0][1] for pt in polygon]), key=operator.itemgetter(1))
    # Bottom-right point has largest (x + y) value
    bottom_right, _ = max(enumerate([pt[0][0] + pt[0][1] for pt in polygon]), key=operator.itemgetter(1))
    # Bottom-left point has smallest (x - y) value
    bottom_left, _ = min(enumerate([pt[0][0] - pt[0][1] for pt in polygon]), key=operator.itemgetter(1))
    
    # Return an array of all 4 points using the indices
    # Each point is in its own array of one coordinate
    return [polygon[top_left][0], polygon[top_right][0], polygon[bottom_right][0], polygon[bottom_left][0]]

def distance_between(p1, p2):
    """
        Returns the scalar distance between two points
    """
    a = np.absolute(p2[0] - p1[0])
    b = np.absolute(p2[1] - p1[1])
    return np.sqrt((a ** 2) + (b ** 2))

def crop_and_warp(img, crop_rect):
    """
        Crops and warps a rectangular section from an image into a square of similar size.
    """
    # Rectangle described by top left, top right, bottom right and bottom left points
    top_left, top_right, bottom_right, bottom_left = crop_rect[0], crop_rect[1], crop_rect[2], crop_rect[3]
    
    # Explicitly set the data type to float32 or `getPerspectiveTransform` will throw an error
    src = np.array([top_left, top_right, bottom_right, bottom_left], dtype='float32')
    
    # Get the longest side in the rectangle
    side = max([
        distance_between(top_left, top_right),
        distance_between(bottom_right, bottom_left),
        distance_between(top_left, bottom_left),
        distance_between(bottom_right, top_right)
    ])
    
    # Describe a square with side of the calculated length, this is the new perspective we want to warp to
    dst = np.array([[0, 0], [side - 1, 0], [side - 1, side - 1], [0, side - 1]], dtype='float32')
    
    # Gets the transformation matrix for skewing the image to fit a square by comparing the 4 before and after points
    matrix = cv2.getPerspectiveTransform(src, dst)
    
    # Performs the transformation on the original image
    return cv2.warpPerspective(img, matrix, (int(side), int(side)))

def extract_board(image_path):
    # load the image 
    original = cv2.imdecode(image_path, cv2.IMREAD_COLOR) 
       
    # convert it to grayscale 
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)

    # preprocess the image
    processed = pre_process_image(gray)
 
    # Finds the 4 extreme corners of the largest contour in the image
    corners = find_corners_of_largest_polygon(processed)
    
    # Crops and warps a rectangular section from an image into a square of similar size
    cropped = crop_and_warp(original, corners)

    return cropped

def pre_process_cropped_image(img):
    proc = cv2.medianBlur(img, 5)
    
    kernel = np.ones((3,3), np.uint8)

    adaptive_th = cv2.adaptiveThreshold(proc.copy(), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    # adaptive_th = cv2.adaptiveThreshold(proc.copy(), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    adaptive_th = cv2.morphologyEx(adaptive_th, cv2.MORPH_OPEN, kernel)
    
    adaptive_th = cv2.morphologyEx(adaptive_th, cv2.MORPH_CLOSE, kernel)
    
    ret, global_th = cv2.threshold(proc.copy(), 127, 255, cv2.THRESH_BINARY_INV)
    global_th = cv2.morphologyEx(global_th, cv2.MORPH_OPEN, kernel)
    global_th = cv2.morphologyEx(global_th, cv2.MORPH_CLOSE, kernel)

    result = cv2.bitwise_or(adaptive_th, global_th)
    result = cv2.morphologyEx(result, cv2.MORPH_OPEN, kernel)
    result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)

    return result

def count_non_zero_pixels(image, x, y, width, height):
    region = image[y:y+height, x:x+width]
    non_zero_pixels = np.count_nonzero(region)
    
    return non_zero_pixels

def getScore(lst):
    if (lst[0][0] == 0): # {lst[0][0] == 0} is 'v'
        if (len(lst) == 1):
            return 'v';
        # elif (len(lst) >= 2):
        #     return ? # must handle this case!
    elif (len(lst) == 2):
        integer_part  = lst[0][0]
        integer_part_score = str(integer_part-1)    

        decimal_part = lst[1][0]
        decimal_part_score = str(decimal_part-12)    
        
        score = integer_part_score + '.' + decimal_part_score  
        
        return score;       

def getIntegerDecimal(lst):
    integer_decimal = 0;
    if (len(lst) >= 3):
        # 
        # => prompt for user to choose   
        integer_decimal = 0 # ?
    elif (len(lst) == 0):
        # => not choose yet
        # => prompt for user to choose
        integer_decimal = 0 # ?
    else:
        integer_decimal = lst[:2]
    
    return integer_decimal   
        
def grade_transcript(img): 
    # convert the cropped image to grayscale 
    gray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)

    # preprocess the cropped image
    processed = pre_process_cropped_image(gray)
    
    h, w, c = img.shape
    number_of_students = int(h/88.05)
    drawn_img = img.copy()
    #1
    x, y, w, h = 17, 12, 30, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;   
    #2
    x, y, w, h = 60, 12, 27, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;
    #3
    x, y, w, h = 93, 12, 30, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;
    #4
    x, y, w, h = 129, 12, 30, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;        
    #5
    x, y, w, h = 164, 12, 29, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;
    #6
    x, y, w, h = 199, 12, 29, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;
    #7
    x, y, w, h = 234, 12, 28, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1) 
        y = y + 88;
    #8
    x, y, w, h = 269, 12, 28, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;
    #9
    x, y, w, h = 304, 12, 28, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;
    #10
    x, y, w, h = 340, 12, 28, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;
    #11
    x, y, w, h = 375, 12, 27, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;    
    #12
    x, y, w, h = 408, 12, 28, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;   
    #13
    x, y, w, h = 451, 12, 28, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;  
    #14
    x, y, w, h = 486, 12, 28, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88; 
    #15
    x, y, w, h = 521, 12, 28, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88; 
    #16
    x, y, w, h = 557, 12, 28, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88; 
    #17
    x, y, w, h = 592, 12, 28, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88; 
    #18
    x, y, w, h = 627, 12, 28, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;
    #19
    x, y, w, h = 662, 12, 28, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;
    #20
    x, y, w, h = 698, 12, 28, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;
    #21
    x, y, w, h = 733, 12, 28, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;
    #22
    x, y, w, h = 768, 12, 28, 72;
    for i in range(0, number_of_students, 1):
        cv2.rectangle(drawn_img, (x,y), (x+w,y+h), (0,0,255), 1)
        y = y + 88;

    positions = [17, 60, 93, 129, 164, 199, 234, 269, 304, 340, 375, 408, 451, 486, 521, 557, 592, 627, 662, 698, 733, 768]
    scores = []
    y = 12
    for n in range(1, number_of_students+1, 1):
        non_zeros_list = []
        for x in positions:
            non_zeros = count_non_zero_pixels(processed, x, y, w, h) #?
            non_zeros_list.append(non_zeros)
        # ...
        pixels_greater_than_1000 = [(index, element) for index, element in enumerate(non_zeros_list) if element > 1000]               
        integer_decimal =  getIntegerDecimal(pixels_greater_than_1000)
        # ...
        score = getScore(integer_decimal)
        scores.append(score)
        y = y + 88;

    return scores;

def writeToExcelFile(data_list, filename, column_name='0'):
    if column_name == '0':
        df = pd.DataFrame(data_list)
    else:
        # Create a DataFrame from the list with the specified column name
        df = pd.DataFrame(data_list, columns=[column_name])

    # Save the DataFrame to an Excel file
    df.to_excel(filename, index=False)

def merge2ExcelFiles(file1, file2, column_name):
    # Read the first Excel file
    df1 = pd.read_excel(file1)

    # Read the second Excel file
    df2 = pd.read_excel(file2)

    # Append the column from file 2 to the right of existing column in file 1
    df1[column_name] = df2
    
    return df1

def exportResult(dssv_path, scores_path):    
    column_name = 'Điểm';
    dssv_scores = merge2ExcelFiles(dssv_path, scores_path, column_name);
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)));
    fileName = "dssv_scores.xlsx";
    dssv_scores_path= os.path.join(root_path, "static", "files", "dssv_scores.xlsx")
    writeToExcelFile(dssv_scores, dssv_scores_path);
    
    fileSize = math.ceil(os.stat(dssv_scores_path).st_size / 1024); # KB
    
    return [fileName, fileSize, dssv_scores_path];

def extractScore(image_path, dssv_path): 
    image_path = np.fromfile(image_path, dtype=np.uint8)
    
    transcript_board = extract_board(image_path)
    
    h, w, c = transcript_board.shape
        
    transcript_board_bubble = transcript_board[95:95+h, 934:934+805]

    scores = grade_transcript(transcript_board_bubble)
    
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scores_path= os.path.join(root_path, "static", "files", "scores.xlsx")
    
    writeToExcelFile(scores, scores_path, "Điểm")

    return exportResult(dssv_path, scores_path)
    
   
