#!/usr/bin/python3
#it created by Carlos Williamberg on 05/29/2017.
import os, sys, time
import tensorflow as tf

from io import BytesIO
from picamera import PiCamera
from PIL import Image
import vs_io

def getPicture():
    stream = BytesIO()#create the in-memory stream
    camera = PiCamera()
    camera.start_preview()
    time.sleep(2)
    camera.capture(stream, format='jpeg')
    stream.seek(0)#"Rewind" the stream to the beginning so we can read its content
    camera.close()
    return stream

def savePicture():
    camera = PiCamera()
    #camera.resolution = (64, 64)
    camera.start_preview()
    time.sleep(2)
    camera.capture('img.jpg')
    camera.stop_preview()
    camera.close()

def main():
    # Loads label file, strips off carriage return
    label_lines = [line.rstrip() for line 
                   in tf.gfile.GFile("retrained_labels.txt")]

    # Unpersists graph from file
    with tf.gfile.FastGFile("retrained_graph.pb", 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')
    for x in range(3):
        vs_io.beep(0.05)
    with tf.Session() as sess:
        while(True):
            #image_data = getPicture()# Read in the image_data
            savePicture()
            image_data = tf.gfile.FastGFile('img.jpg', 'rb').read()
            
            # Feed the image_data as input to the graph and get first prediction
            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
            #start_time = time.time()
    
            predictions = sess.run(softmax_tensor, \
             {'DecodeJpeg/contents:0': image_data})
            #final = (time.time() - start_time)
            #print("-- %s seconds ---" % final)
            # Sort to show labels of first prediction in order of confidence
            top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
            human_string = label_lines[top_k[0]]
            score = predictions[0][top_k[0]]
            if (human_string == "faixapedestre" and score > 0.8):
                vs_io.notification()
            #for node_id in top_k:
                #human_string = label_lines[node_id]
                #score = predictions[0][node_id]
            #print('%s (score = %.5f)' % (human_string, score))

if __name__ == '__main__':main()
