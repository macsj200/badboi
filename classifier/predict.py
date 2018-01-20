from Classification2.getbottleneck import get_bottleneck
import tensorflow as tf
import numpy as np
from Classification2.keys import KEYS
import pandas as pd
from tensorflow.python.platform import gfile
import os
import json
from Classification2.producebottlenecks import producebottlenecks
import urllib
import base64

model_dir = 'Saved_models/'

def predict_type(bottleneck_values):
	tf.reset_default_graph()
	with tf.Session() as sess:
		saver = tf.train.import_meta_graph(model_dir+'Clothing_types/Clothing_types.meta')
		saver.restore(sess, tf.train.latest_checkpoint(model_dir+'Clothing_types'))
		prediction = sess.graph.get_tensor_by_name('prediction:0')
		inputs = sess.graph.get_tensor_by_name('inputs:0')
		pred = sess.run(prediction, feed_dict={inputs: bottleneck_values})
	index = np.argmax(pred)
	return index

def predict_x(attributes, bottleneck_values, single=True):
	tf.reset_default_graph()
	with tf.Session() as sess:
		saver = tf.train.import_meta_graph(model_dir+attributes+'/'+attributes+'.meta')
		saver.restore(sess, tf.train.latest_checkpoint(model_dir+attributes))
		prediction = sess.graph.get_tensor_by_name('prediction:0')
		inputs = sess.graph.get_tensor_by_name('inputs:0')
		pred = sess.run(prediction, feed_dict={inputs: bottleneck_values})
	if single:
		index = np.argmax(pred)
		return KEYS[attributes][index]
	else:
		pred = pred[0]
		info = []
		pred = np.round(pred)
		for i in range(len(pred)):
			if pred[i] == 1:
				info.append(KEYS[attributes][i])
		return info

def predict_x_2(attributes, bottleneck_values, single=True):
	tf.reset_default_graph()
	with tf.Session() as sess:
		saver = tf.train.import_meta_graph(model_dir+attributes+'/'+attributes+'.meta')
		saver.restore(sess, tf.train.latest_checkpoint(model_dir+attributes))
		prediction = sess.graph.get_tensor_by_name('prediction:0')
		inputs = sess.graph.get_tensor_by_name('inputs:0')
		pred = sess.run(prediction, feed_dict={inputs: bottleneck_values})
	return pred

def predict_top(bottleneck_values):
	summary = {}
	summary['Clothing type'] = 'Top'
	summary['Top primary colour'] = predict_x('Top_primary_colours', bottleneck_values)
	summary['Top secondary colour'] = predict_x('Top_secondary_colours', bottleneck_values)
	top_type = predict_x('Top_types', bottleneck_values)
	summary['Top type'] = top_type
	if 't-' in summary['Top type'] or 'singlet' in summary['Top type'] or 'polo' in summary['Top type']:
		summary['T-shirt style'] = predict_x('T-shirt_styles', bottleneck_values, False)
		summary['T-shirt fit'] = predict_x('T-shirt_fits', bottleneck_values)
	else:
		summary['Shirt style'] = predict_x('Shirt_styles', bottleneck_values, False)
		summary['Shirt fit'] = predict_x('Shirt_fits', bottleneck_values)
	summary['Top pattern'] = predict_x('Top_patterns', bottleneck_values, False)
	summary['Top material'] = predict_x('Top_materials', bottleneck_values)

	summary['Type'] = 

	return summary

def predict_top_vector(bottleneck_values):
	top_primary = predict_x_2('Top_primary_colours', bottleneck_values)[0].tolist()
	top_secondary = predict_x_2('Top_secondary_colours', bottleneck_values)[0].tolist()
	top_type = predict_x_2('Top_types', bottleneck_values)[0].tolist()
	actual_type = predict_x('Top_types', bottleneck_values)
	if 't-' in actual_type or 'singlet' in actual_type or 'polo' in actual_type:
		t_shirt_style = predict_x_2('T-shirt_styles', bottleneck_values, False)[0].tolist()
		t_shirt_fit = predict_x_2('T-shirt_fits', bottleneck_values)[0].tolist()
		shirt_style = [0,0,0,0,0]
		shirt_fit = [0,0]
	else:
		shirt_style = predict_x_2('Shirt_styles', bottleneck_values, False)[0].tolist()
		shirt_fit = predict_x_2('Shirt_fits', bottleneck_values)[0].tolist()
		t_shirt_style = [0,0,0,0,0]
		t_shirt_fit = [0,0,0,0]
	top_pattern = predict_x_2('Top_patterns', bottleneck_values, False)[0].tolist()
	top_material = predict_x_2('Top_materials', bottleneck_values)[0].tolist()
	combined = top_primary + top_secondary + top_type + t_shirt_style + t_shirt_fit + shirt_style + shirt_fit + top_pattern + top_material
	return combined

def predict_bottom(bottleneck_values):
	summary = {}
	summary['Clothing type'] = 'Bottom'
	summary['Bottom primary colour'] = predict_x('Bottom_primary_colours', bottleneck_values)
	summary['Bottom secondary colour'] = predict_x('Bottom_secondary_colours', bottleneck_values)
	summary['Bottom type'] = predict_x('Bottom_types', bottleneck_values)
	summary['Bottom material'] = predict_x('Bottom_materials', bottleneck_values)
	if 'denim' in summary['Bottom material']:
		summary['Denim style'] = predict_x('Denim_styles', bottleneck_values, False)
	summary['Bottom patterns'] = predict_x('Bottom_patterns', bottleneck_values, False)
	summary['Bottom style'] = predict_x('Bottom_styles', bottleneck_values)
	summary['Bottom fit'] = predict_x('Bottom_fits', bottleneck_values)
	return summary

def predict_bottom_vector(bottleneck_values):
	bottom_pri = predict_x_2('Bottom_primary_colours', bottleneck_values)[0].tolist()
	bottom_sec = predict_x_2('Bottom_secondary_colours', bottleneck_values)[0].tolist()
	bottom_type = predict_x_2('Bottom_types', bottleneck_values)[0].tolist()
	bottom_material = predict_x_2('Bottom_materials', bottleneck_values)[0].tolist()
	actual_material = predict_x('Bottom_materials', bottleneck_values)
	if 'denim' in actual_material:
		denim_style = predict_x_2('Denim_styles', bottleneck_values, False)[0].tolist()
	else:
		denim_style = [0,0,0]
	bottom_pattern = predict_x_2('Bottom_patterns', bottleneck_values, False)[0].tolist()
	bottom_style = predict_x_2('Bottom_styles', bottleneck_values)[0].tolist()
	bottom_fit = predict_x_2('Bottom_fits', bottleneck_values)[0].tolist()
	combined = bottom_pri+bottom_sec+bottom_type+bottom_material+denim_style+bottom_pattern+bottom_style+bottom_fit
	return combined

def predict_shoe(bottleneck_values):
	summary = {}
	summary['Clothing type'] = 'Shoe'
	summary['Shoe primary colour'] = predict_x('Shoe_primary_colours', bottleneck_values)
	summary['Shoe secondary colour'] = predict_x('Shoe_secondary_colours', bottleneck_values)
	summary['Shoe type'] = predict_x('Shoe_types', bottleneck_values)
	summary['Shoe feature'] = predict_x('Shoe_features', bottleneck_values, False)
	summary['Shoe material'] = predict_x('Shoe_materials', bottleneck_values, False)
	return summary

def predict_shoe_vector(bottleneck_values):
	shoe_pri = predict_x_2('Shoe_primary_colours', bottleneck_values)[0].tolist()
	shoe_sec = predict_x_2('Shoe_secondary_colours', bottleneck_values)[0].tolist()
	shoe_type = predict_x_2('Shoe_types', bottleneck_values)[0].tolist()
	shoe_feature = predict_x_2('Shoe_features', bottleneck_values, False)[0].tolist()
	shoe_material = predict_x_2('Shoe_materials', bottleneck_values, False)[0].tolist()
	combined = shoe_pri+shoe_sec+shoe_type+shoe_feature+shoe_material
	return combined

def predict(bottleneck_values, clothing_type=None):
	if clothing_type is None:
		clothing_type = predict_type(bottleneck_values)
	if clothing_type == 0:
		output = predict_top(bottleneck_values)
	elif clothing_type == 1:
		output = predict_bottom(bottleneck_values)
	elif clothing_type == 2:
		output = predict_shoe(bottleneck_values)
	return output
	# TODO: package results into nice message

def predict_vector(image_url): # used to output predicted vector
	urllib.urlretrieve(image_url, 'query_image.jpg')
	# pic = Image.open('query_image.jpg')
	# pic.save('query_image.jpg',quality=40,optimize=True)

	bottleneck_values = get_bottleneck('query_image.jpg')
	clothing_type = predict_type(bottleneck_values)
	# response = {}
	if clothing_type == 0:
		#response['type'] = 'tops'
		x = predict_top_vector(bottleneck_values)
	elif clothing_type == 1:
		#response['type'] = 'bottoms'
		x = predict_bottom_vector(bottleneck_values)
	elif clothing_type == 2:
		#response['type'] = 'shoes'
		x = predict_shoe_vector(bottleneck_values)
	return x

'''
function to be called to generate wardrobe. 
returns (list of tops, list of bottoms, list of shoes).
SHOULD IT RETURN BYTE STRING IMAGE OF CROPPED CLOTHES?
'''
def feed_dir(image_dir):
	producebottlenecks(image_dir) # this will also create the bottleneck folder
	path = os.path.join('bottlenecks/', image_dir)

	tops_list = []
	file_glob = os.path.join(path, '*top.jpg.txt')
	tops_list.extend(gfile.Glob(file_glob))

	bottoms_list = []
	file_glob = os.path.join(path, '*bottom.jpg.txt')
	bottoms_list.extend(gfile.Glob(file_glob))

	shoes_list = []
	file_glob = os.path.join(path, '*shoe.jpg.txt')
	shoes_list.extend(gfile.Glob(file_glob))

	tops = []
	for top in tops_list:
		bottleneck_file = open(top, 'r')
		bottleneck_string = bottleneck_file.read()
		bottleneck_values = [float(x) for x in bottleneck_string.split(',')]
		bottleneck_values = np.reshape(bottleneck_values, (1, 2048))
		summary = predict(bottleneck_values, 0)
		summary['image_dir'] = top[12:-4]
		with open(summary['image_dir'], "rb") as imageFile:
			string = base64.b64encode(imageFile.read())
		summary['image_string'] = string
		tops.append(summary)

	bottoms = []
	for bottom in bottoms_list:
		bottleneck_file = open(bottom, 'r')
		bottleneck_string = bottleneck_file.read()
		bottleneck_values = [float(x) for x in bottleneck_string.split(',')]
		bottleneck_values = np.reshape(bottleneck_values, (1, 2048))
		summary = predict(bottleneck_values, 1)
		summary['image_dir'] = bottom[12:-4]
		with open(summary['image_dir'], "rb") as imageFile:
			string = base64.b64encode(imageFile.read())
		summary['image_string'] = string
		bottoms.append(summary)

	shoes = []
	for shoe in shoes_list:
		bottleneck_file = open(shoe, 'r')
		bottleneck_string = bottleneck_file.read()
		bottleneck_values = [float(x) for x in bottleneck_string.split(',')]
		bottleneck_values = np.reshape(bottleneck_values, (1, 2048))
		summary = predict(bottleneck_values, 2)
		summary['image_dir'] = shoe[12:-4]
		with open(summary['image_dir'], "rb") as imageFile:
			string = base64.b64encode(imageFile.read())
		summary['image_string'] = string
		shoes.append(summary)

	response = {}
	response['tops'] = tops
	response['bottoms'] = bottoms
	response['shoes'] = shoes
	return response



####################################################################################
import glob
import itertools
import csv
from progress.bar import Bar
if __name__ == '__main__':
	# image = 'pics/tshirt.jpg'
	#image = 'pics/pants.jpg'
	# image = 'pics/group-photo-02.jpg-shoe.jpg'
	# bottleneck_values = get_bottleneck(image)
	# print (predict(bottleneck_values))
	# print (predict_top_2(bottleneck_values))
	# print (len(predict_top_2(bottleneck_values)))
	
	# result = feed_dir('USERS/b00c6a39-7807-4cf2-9a04-6b41f2efcf18 wardrobe')
	# print (result)

	# image = 'USERS/b00c6a39-7807-4cf2-9a04-6b41f2efcf18 wardrobe/1-bottom.jpg'
	# bottleneck_values = get_bottleneck(image)
	# result = predict_bottom(bottleneck_values)
	# print (result)

	# result = predict_vector('https://jafrianews.files.wordpress.com/2012/05/russian-president-putin-with-vladimir-putin-may-7-2012.jpg')
	# print (result)
	# print (len(result['vector']))

	x = predict_vector('https://firebasestorage.googleapis.com/v0/b/yuxapp-84210.appspot.com/o/1%2F513414925842.jpg?alt=media&token=4c59e9c9-6fa8-4720-99c7-977bae71e9f5')
	print (x)

	'''
	path = 'bottlenecks/Unlabelled Clothes/Tops/'
	files = glob.glob(path+'*.txt')
	
	all_bottlenecks = []
	bottleneck_paths = []
	bar = Bar('pri: ', max=len(files))
	for bottleneck_path in files:
		bottleneck_paths.append(bottleneck_path)
		bottleneck_file = open(bottleneck_path, 'r')
		bottleneck_string = bottleneck_file.read()
		bottleneck_values = [float(x) for x in bottleneck_string.split(',')]
		all_bottlenecks.append(bottleneck_values)
		bar.next()
	bar.finish()
	bottleneck_paths = np.asarray(bottleneck_paths)
	bottleneck_paths = np.reshape(bottleneck_paths, (len(bottleneck_paths), 1))

	top_primary = predict_x_2('Top_primary_colours', all_bottlenecks)
	top_secondary = predict_x_2('Top_secondary_colours', all_bottlenecks)
	top_type = predict_x_2('Top_types', all_bottlenecks)
	t_shirt_style = predict_x_2('T-shirt_styles', all_bottlenecks)
	t_shirt_fit = predict_x_2('T-shirt_fits', all_bottlenecks)
	shirt_style = predict_x_2('Shirt_styles', all_bottlenecks)
	shirt_fit = predict_x_2('Shirt_fits', all_bottlenecks)
	top_pattern = predict_x_2('Top_patterns', all_bottlenecks)
	top_material = predict_x_2('Top_materials', all_bottlenecks)

	x = np.concatenate((bottleneck_paths, top_primary, top_secondary, top_type, t_shirt_style, t_shirt_fit, shirt_style, shirt_fit, top_pattern, top_material), axis=1)
	print (len(x))
	print (x.shape)

	df = pd.DataFrame(x)
	df.to_csv('unlabelled_predictedtops.csv')
	'''

		# top_type = list(predict_x_2('Top_types', bottleneck_values)[0])
		# actual_type = predict_x('Top_types', bottleneck_values)
		# if 't-' in actual_type or 'singlet' in actual_type or 'polo' in actual_type:
		# 	t_shirt_style = list(predict_x_2('T-shirt_styles', bottleneck_values, False)[0])
		# 	t_shirt_fit = list(predict_x_2('T-shirt_fits', bottleneck_values)[0])
		# 	shirt_style = [0,0,0,0,0]
		# 	shirt_fit = [0,0]
		# else:
		# 	shirt_style = list(predict_x_2('Shirt_styles', bottleneck_values, False)[0])
		# 	shirt_fit = list(predict_x_2('Shirt_fits', bottleneck_values)[0])
		# 	t_shirt_style = [0,0,0,0,0]
		# 	t_shirt_fit = [0,0,0,0]
		# top_pattern = list(predict_x_2('Top_patterns', bottleneck_values, False)[0])
		# top_material = list(predict_x_2('Top_materials', bottleneck_values)[0])


		# total = list(itertools.chain(top_primary, top_secondary, top_type, t_shirt_style, t_shirt_fit, shirt_style, shirt_fit, top_pattern, top_material))
		# total = [bottleneck_path]+top_primary + top_secondary + top_type + t_shirt_style + t_shirt_fit + shirt_style + shirt_fit + top_pattern + top_material

	# with open('clean_predictedtops.csv', 'a') as csvfile:
	# 	writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	# 	writer.writerow(x)

	'''
	path = 'bottlenecks/Unlabelled Clothes/Bottoms/'
	files = glob.glob(path+'*.txt')
	
	all_bottlenecks = []
	bottleneck_paths = []
	bar = Bar('bottlenecks: ', max=len(files))
	for bottleneck_path in files:
		bottleneck_paths.append(bottleneck_path)
		bottleneck_file = open(bottleneck_path, 'r')
		bottleneck_string = bottleneck_file.read()
		bottleneck_values = [float(x) for x in bottleneck_string.split(',')]
		all_bottlenecks.append(bottleneck_values)
		bar.next()
	bar.finish()
	bottleneck_paths = np.asarray(bottleneck_paths)
	bottleneck_paths = np.reshape(bottleneck_paths, (len(bottleneck_paths), 1))

	a = predict_x_2('Bottom_primary_colours', all_bottlenecks)
	b = predict_x_2('Bottom_secondary_colours', all_bottlenecks)
	c = predict_x_2('Bottom_types', all_bottlenecks)
	d = predict_x_2('Bottom_materials', all_bottlenecks)
	e = predict_x_2('Denim_styles', all_bottlenecks)
	f = predict_x_2('Bottom_patterns', all_bottlenecks)
	g = predict_x_2('Bottom_styles', all_bottlenecks)
	h = predict_x_2('Bottom_fits', all_bottlenecks)

	x = np.concatenate((bottleneck_paths, a, b, c, d, e, f, g, h), axis=1)
	print (len(x))
	print (x.shape)

	df = pd.DataFrame(x)
	df.to_csv('unlabelled_predictedbottoms.csv')
	'''


	# path = 'bottlenecks/Clothes/Bottoms/'
	# files = glob.glob(path+'*.txt')

	# files = files[:5]
	# for bottleneck_path in files:
	# 	bottleneck_file = open(bottleneck_path, 'r')
	# 	bottleneck_string = bottleneck_file.read()
	# 	bottleneck_values = [float(x) for x in bottleneck_string.split(',')]
	# 	bottleneck_values = np.reshape(bottleneck_values, (1,2048))

	# 	bottom_pri = list(predict_x_2('Bottom_primary_colours', bottleneck_values)[0])
	# 	bottom_sec = list(predict_x_2('Bottom_secondary_colours', bottleneck_values)[0])
	# 	bottom_type = list(predict_x_2('Bottom_types', bottleneck_values)[0])
	# 	bottom_material = list(predict_x_2('Bottom_materials', bottleneck_values)[0])
	# 	actual_material = predict_x('Bottom_materials', bottleneck_values)
	# 	if 'denim' in actual_material:
	# 		denim_style = list(predict_x_2('Denim_styles', bottleneck_values, False)[0])
	# 	else:
	# 		denim_style = [0,0,0]
	# 	bottom_pattern = list(predict_x_2('Bottom_patterns', bottleneck_values, False)[0])
	# 	bottom_style = list(predict_x_2('Bottom_styles', bottleneck_values)[0])
	# 	bottom_fit = list(predict_x_2('Bottom_fits', bottleneck_values)[0])


	# 	total = bottom_pri+bottom_sec+bottom_type+bottom_material+denim_style+bottom_pattern+bottom_style+bottom_fit


	# 	with open('testbottoms.csv', 'a') as csvfile:
	# 		writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	# 		writer.writerow(total)

	'''
	path = 'bottlenecks/Unlabelled Clothes/Shoes/'
	files = glob.glob(path+'*.txt')
	
	all_bottlenecks = []
	bottleneck_paths = []
	bar = Bar('bottlenecks: ', max=len(files))
	for bottleneck_path in files:
		bottleneck_paths.append(bottleneck_path)
		bottleneck_file = open(bottleneck_path, 'r')
		bottleneck_string = bottleneck_file.read()
		bottleneck_values = [float(x) for x in bottleneck_string.split(',')]
		all_bottlenecks.append(bottleneck_values)
		bar.next()
	bar.finish()
	bottleneck_paths = np.asarray(bottleneck_paths)
	bottleneck_paths = np.reshape(bottleneck_paths, (len(bottleneck_paths), 1))

	a = predict_x_2('Shoe_primary_colours', all_bottlenecks)
	b = predict_x_2('Shoe_secondary_colours', all_bottlenecks)
	c = predict_x_2('Shoe_types', all_bottlenecks)
	d = predict_x_2('Shoe_features', all_bottlenecks)
	e = predict_x_2('Shoe_materials', all_bottlenecks)

	x = np.concatenate((bottleneck_paths, a, b, c, d, e), axis=1)
	print (len(x))
	print (x.shape)

	df = pd.DataFrame(x)
	df.to_csv('unlabelled_predictedshoes.csv')
	'''

	# path = 'bottlenecks/Clothes/Shoes/'
	# files = glob.glob(path+'*.txt')
	# bar = Bar('shoes: ', max=len(files))
	# for bottleneck_path in files:
	# 	bottleneck_file = open(bottleneck_path, 'r')
	# 	bottleneck_string = bottleneck_file.read()
	# 	bottleneck_values = [float(x) for x in bottleneck_string.split(',')]
	# 	bottleneck_values = np.reshape(bottleneck_values, (1,2048))

	# 	shoe_pri = list(predict_x_2('Shoe_primary_colours', bottleneck_values)[0])
	# 	shoe_sec = list(predict_x_2('Shoe_secondary_colours', bottleneck_values)[0])
	# 	shoe_type = list(predict_x_2('Shoe_types', bottleneck_values)[0])
	# 	shoe_feature = list(predict_x_2('Shoe_features', bottleneck_values, False)[0])
	# 	shoe_material = list(predict_x_2('Shoe_materials', bottleneck_values, False)[0])

	# 	total = [bottleneck_path]+shoe_pri+shoe_sec+shoe_type+shoe_feature+shoe_material

	# 	with open('testshoes.csv', 'a') as csvfile:
	# 		writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	# 		writer.writerow(total)
	# 	bar.next()
	# bar.finish()
