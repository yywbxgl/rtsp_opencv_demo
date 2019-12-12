
import tensorflow as tf
import sys
import datetime
sys.path.append("../")
from train_models.MTCNN_config import config


class FcnDetector(object):
    #net_factory: which net
    #model_path: where the params'file is
    def __init__(self, net_factory, model_path):
        #create a graph
        graph = tf.Graph()
        with graph.as_default():
       	    # output_graph_def = tf.GraphDef()
            # model_pb = model_path + '.pb'
            # print(model_pb)
            # with tf.gfile.GFile(model_pb, 'rb') as f:
            #     output_graph_def.ParseFromString(f.read())
            #     tf.import_graph_def(output_graph_def, name="")
            #define tensor and op in graph(-1,1)
            self.image_op = tf.placeholder(tf.float32, name='input_image')
            self.width_op = tf.placeholder(tf.int32, name='image_width')
            self.height_op = tf.placeholder(tf.int32, name='image_height')
            image_reshape = tf.reshape(self.image_op, [1, self.height_op, self.width_op, 3])
            #self.cls_prob batch*2
            #self.bbox_pred batch*4
            #construct model here
            #self.cls_prob, self.bbox_pred = net_factory(image_reshape, training=False)
            #contains landmark
            self.cls_prob, self.bbox_pred, _ = net_factory(image_reshape, training=False)

            
            #allow 
            self.sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True, gpu_options=tf.GPUOptions(allow_growth=True)))
            # 需要有一个初始化的过程
            # self.sess.run(tf.global_variables_initializer())
            # init_g = tf.global_variables_initializer()
            #
            # self.sess.run(init_g)
            saver = tf.train.Saver()
            #check whether the dictionary is valid
            model_dict = '/'.join(model_path.split('/')[:-1])
            ckpt = tf.train.get_checkpoint_state(model_dict)
            print(model_path)
            readstate = ckpt and ckpt.model_checkpoint_path
            assert  readstate, "the params dictionary is not valid"
            print("restore models' param")
            saver.restore(self.sess, model_path)
    def predict(self, databatch):
        height, width, _ = databatch.shape
        # print(height, width)
        begin = datetime.datetime.now()
        cls_prob, bbox_pred = self.sess.run([self.cls_prob, self.bbox_pred],
                                                           feed_dict={self.image_op: databatch, self.width_op: width,
                                                                      self.height_op: height})
        end = datetime.datetime.now()
        run_K = end - begin
        # print("fcn_time: ", run_K.total_seconds() * 1000)
        return cls_prob, bbox_pred
