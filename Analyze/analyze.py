import os
import io
import cv2
import sys

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "My First Project-17c2b113ec1d.json"

def transcribe_file(speech_file):
    """Transcribe the given audio file."""
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()

    audio = types.RecognitionAudio(content=content)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        #sample_rate_hertz=1600,
        language_code='en-US')
    
    response = client.recognize(config, audio)
    result = response.results[0]
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    return result.alternatives[0].transcript

def analyze_file(text):
    from google.cloud import language
    from google.cloud.language import enums
    from google.cloud.language import types
    # Instantiates a client
    client = language.LanguageServiceClient()

    # The text to analyze
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    # Detects the sentiment of the text
    sentiment = client.analyze_sentiment(document=document).document_sentiment

    #print('Text: {}'.format(text))
    #print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))
    return sentiment.magnitude, sentiment.score

# The name of the image file to annotate
file_name = sys.argv[1][:-4]

# Names of likelihood from google.cloud.vision.enums
likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                   'LIKELY', 'VERY_LIKELY')
# emotes from the speech to text io
def emotes_s(magnitude, score):
    surprise = (magnitude > score) and (score > 0)
    joy = score > 0
    sad = score < 0
    anger = (abs(score) < magnitude) and (score < 0)
    return (surprise, joy, sad, anger)

# emotes from the vision io
def emotes_v(path):
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.face_detection(image=image)
    faces = response.face_annotations
    for face in faces:
            if(face.anger_likelihood>=4):
                mAnger=1
            elif(face.anger_likelihood==3):
                mAnger=0.5
            else:
                mAnger=0
            if (face.sorrow_likelihood>= 4):
                mSorrow = 1
            elif (face.sorrow_likelihood== 3):
                mSorrow = 0.5
            else:
                mSorrow = 0
            if(face.surprise_likelihood>=4):
                mSurprise=1
            elif(face.surprise_likelihood==3):
                mSurprise=0.5
            else:
                mSurprise=0
            if(face.joy_likelihood>=4):
                mJoy=1
            elif(face.joy_likelihood==3):
                mJoy=0.5
            else:
                mJoy=0
    return(mSurprise, mJoy, mSorrow, mAnger)

# matching vemotions to semotions at specific times
def match(magnitude, score, path, mCtr, surpriseCtr, joyCtr, angerCtr, sorrowCtr):
    ssurprise, sjoy, ssorrow, sanger = emotes_s(magnitude, score)
    vsurprise, vjoy, vsorrow, vanger = emotes_v(path)
    if (ssurprise == vsurprise):
        mCtr +=1
    else:
        surpriseCtr+=1
    if (sjoy == vjoy):
        mCtr += 1
    else:
        joyCtr += 1
    if (sanger == vanger):
        mCtr += 1
    else:
        angerCtr += 1
    if (ssorrow == vsorrow):
        mCtr +=1
    else:
        sorrowCtr += 1
    if (vsurprise==0.5 or vjoy==0.5 or vsorrow==0.5 or vanger==0.5):
        mCtr+=0.5
    return (mCtr, surpriseCtr, joyCtr, sorrowCtr, angerCtr)

# offest angle determined
def angleOg(first):
    from google.cloud import vision
    from google.cloud.vision import types
    client = vision.ImageAnnotatorClient()

    with io.open(first, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.face_detection(image=image)
    faces = response.face_annotations[0]
    originalTilt = faces.tilt_angle
    originalPan = faces.pan_angle
    return (originalTilt, originalPan)

# creates offset angles based on the frame we are checking
def angleNew(path, ogTilt, ogPan):
    from google.cloud import vision
    from google.cloud.vision import types
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.face_detection(image=image)
    faces = response.face_annotations[0]
    nTilt = faces.tilt_angle - ogTilt
    nPan = faces.pan_angle - ogPan
    return (nTilt, nPan)

# creates a difference from the frame after the one we are checking with angleNew
def panDiff(path, ogPan, nPan):
    from google.cloud import vision
    from google.cloud.vision import types
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.face_detection(image=image)
    faces = response.face_annotations[0]
    PanDiff = faces.pan_angle - ogPan - nPan
    return PanDiff

# increases a ctr based on a boolean condition
def panCtr(PanDiff1, PanDiff2, ctr):
    if ((PanDiff1<0 and PanDiff2>0) or (PanDiff1>0 and PanDiff2<0)):
        ctr +=1
    return ctr

# increases a tilt ctr based on a boolean condition
def tiltCtr(nTilt, ctr):
    if (nTilt<-.1):
        ctr+=1
    return ctr

# returns total angle score
def angleScore(panCtr, tiltCtr, totalTime):
    ideal = int(round(.2*totalTime))
    panscore = max(0, 25-(25/ideal)*(abs(panCtr-ideal)))
    tiltscore= 15-15*(tiltCtr/totalTime)
    scoreTotal = panscore + tiltscore
    return scoreTotal

# returns total emotion score
def emotionScore(mCtr, numFrames):
    return 60*(mCtr/(numFrames*4))
# gives pretentious advice based on emotions
def pretentiousadvice(surpriseCtr, joyCtr, sorrowCtr, angerCtr):
    before = 0
    if surpriseCtr == joyCtr == surpriseCtr == angerCtr == 0:
        return " Very logical Mr. Spock, way to control your emotions! "
    if surpriseCtr >= joyCtr and surpriseCtr >= sorrowCtr and surpriseCtr >= angerCtr:
        print("Act more surprised!")
        before += 1
    if joyCtr >= surpriseCtr and joyCtr >= sorrowCtr and joyCtr >= angerCtr:
        if before == 1:
            before -= 1
            print("Also ")
        print("Express your joy more!")
        before += 1
    if sorrowCtr >= joyCtr and sorrowCtr >= surpriseCtr and sorrowCtr >= angerCtr:
        if before == 1:
            before -= 1
            print("Also ")
        print("Sympathize better!")
        before += 1
    if angerCtr >= joyCtr and angerCtr >= sorrowCtr and angerCtr >= surpriseCtr:
        if before == 1:
            before -= 1
            print("Also ")
        print("Add some passion to your words!")
        before += 1
    if before == 1:
        return " But overall, job well done!"
    else:
        return " Very logical Mr. Spock, way to control your emotions! "
#def advice()
def angleAdvice(TiltScore, PanScore, totalTime):
    if TiltScore > (totalTime/3):
        return ("Here's a hint: memorize your speech.")
    if PanScore > int(round((totalTime*0.2))):
        return ("Movements are distracting, slow down a bit.")
    if PanScore < int(round((totalTime*0.2))):
        return ("Make sure to pan the crowd.")
    return "Good head movement!"

filepath = 'images/' + file_name
(tiltOg, panOg) = angleOg(filepath + '/frame0.jpg')

MAT = 0
SUP = 0
JOY = 0
SOR = 0
ANG = 0
PAN = 0
TIL = 0

vidcap = cv2.VideoCapture("uploads/" + file_name + '.mp4')
time = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)/vidcap.get(cv2.CAP_PROP_FPS)
#print(time)
(mag, sent) = analyze_file(transcribe_file('audio/mono/' + file_name + '.flac'))
i = 0
while True:
    try:
        #print(i)
        (mCtr, supCtr, joyCtr, sorCtr, angCtr) = match(mag, sent, filepath + '/frame{}.jpg'.format(i), MAT, SUP, JOY, SOR, ANG)
        MAT = mCtr
        SUP = supCtr
        JOY = joyCtr
        SOR = sorCtr
        ANG = angCtr

        (newTilt, newPan) = angleNew(filepath + '/frame{}.jpg'.format(i), tiltOg, panOg)

        try:
            pDiff1 = panDiff(filepath + '/frame{}.jpg'.format(i+1), panOg, newPan)
            pDiff2 = panDiff(filepath + '/frame{}.jpg'.format(i+2), panOg, newPan)
            PAN = panCtr(pDiff1, pDiff2, PAN)
            #print(str(pDiff1) + "   " + str(pDiff2))
        except FileNotFoundError:
            pass

        TIL = tiltCtr(newTilt, TIL)
        #print(TIL)
        i+=1
        #print(MAT)
    except FileNotFoundError:
        break;
#print("SUR: {}  JOY: {}  SOR: {}  ANG: {}".format(SUR, JOY, SOR, ANG))
print("{1}{2}<br>Speaker Effectiveness Rating (SER): {0:.2f}".format(angleScore(PAN, TIL, time) + emotionScore(MAT, i), angleAdvice(TIL, PAN, time), pretentiousadvice(SUP, JOY, SOR, ANG)))