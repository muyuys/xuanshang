# -*- coding: UTF-8 -*-
"""
使用训练完成的模型进行预测
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import sys
import os
import re
import tensorflow as tf
import uuid
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename

model_dir = '/root/test/'  # 模型所在文件夹路径

#将类别ID转换为人类易读的标签


class NodeLookup(object):
  def __init__(self,
               label_lookup_path=None,
               uid_lookup_path=None):
    if not label_lookup_path:
      label_lookup_path = os.path.join(
          model_dir, 'imagenet_2012_challenge_label_map_proto.pbtxt')
    if not uid_lookup_path:
      uid_lookup_path = os.path.join(
          model_dir, 'imagenet_synset_to_human_label_map.txt')
    self.node_lookup = self.load(label_lookup_path, uid_lookup_path)

  def load(self, label_lookup_path, uid_lookup_path):
    if not tf.gfile.Exists(uid_lookup_path):
      tf.logging.fatal('File does not exist %s', uid_lookup_path)
    if not tf.gfile.Exists(label_lookup_path):
      tf.logging.fatal('File does not exist %s', label_lookup_path)

    # Loads mapping from string UID to human-readable string
    proto_as_ascii_lines = tf.gfile.GFile(uid_lookup_path).readlines()
    uid_to_human = {}
    p = re.compile(r'[n\d]*[ \S,]*')
    for line in proto_as_ascii_lines:
      parsed_items = p.findall(line)
      uid = parsed_items[0]
      human_string = parsed_items[2]
      uid_to_human[uid] = human_string

    # Loads mapping from string UID to integer node ID.
    node_id_to_uid = {}
    proto_as_ascii = tf.gfile.GFile(label_lookup_path).readlines()
    for line in proto_as_ascii:
      if line.startswith('  target_class:'):
        target_class = int(line.split(': ')[1])
      if line.startswith('  target_class_string:'):
        target_class_string = line.split(': ')[1]
        node_id_to_uid[target_class] = target_class_string[1:-2]

    # Loads the final mapping of integer node ID to human-readable string
    node_id_to_name = {}
    for key, val in node_id_to_uid.items():
      if val not in uid_to_human:
        tf.logging.fatal('Failed to locate: %s', val)
      name = uid_to_human[val]
      node_id_to_name[key] = name

    return node_id_to_name

  def id_to_string(self, node_id):
    if node_id not in self.node_lookup:
      return ''
    return self.node_lookup[node_id]

#读取训练好的Inception-v3模型来创建graph


def create_graph():
  with tf.gfile.GFile(os.path.join(
          model_dir, 'classify_image_graph_def.pb'), 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    tf.import_graph_def(graph_def, name='')


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/infer', methods=['POST'])
def infer():
    f = request.files['img']

    # 保存图片
    save_father_path = 'images'
    img_path = os.path.join(save_father_path, str(
        uuid.uuid1()) + '.' + secure_filename(f.filename).split('.')[-1])
    if not os.path.exists(save_father_path):
        os.makedirs(save_father_path)
    f.save(img_path)

    # 开始预测图片
    image_data = tf.gfile.FastGFile(img_path, 'rb').read()

    #创建graph
    create_graph()

    sess = tf.Session()
    #Inception-v3模型的最后一层softmax的输出
    softmax_tensor = sess.graph.get_tensor_by_name('softmax:0')
    #输入图像数据，得到softmax概率值（一个shape=(1,1008)的向量）
    predictions = sess.run(
        softmax_tensor, {'DecodeJpeg/contents:0': image_data})
    #(1,1008)->(1008,)
    predictions = np.squeeze(predictions)

    # ID --> English string label.
    node_lookup = NodeLookup()
    #取出概率最大的值
    top = predictions.argsort()[-1:][::-1]
    human_string = node_lookup.id_to_string(top[0])
    score = predictions[top[0]]

    sess.close()

    r = '{"label":%s, "possibility":%.5f}' % (human_string, score)
    print(r)
    return r


if __name__ == '__main__':
    # 启动服务，并指定端口号
    app.run(host='0.0.0.0', port=5000)
