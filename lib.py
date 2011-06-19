import wx
import Image

import numpy as np
import pywt

def transform(image, wavelet='haar', level=1):
	# wx.Image => PIL
	img = Image.new( 'RGB', ( image.GetWidth(), image.GetHeight() ) )
	img.fromstring( image.GetData() )

	# preprocess
	print ' * transform with <%s> level %d' % (wavelet, level)
	img = img.convert('L')
	buf = np.array(img)

	# process
	buf = process(buf, wavelet, level)

	# postprocess
	img = Image.fromarray(buf)

	# PIL => wx.Image
	image = wx.EmptyImage( img.size[0], img.size[1] )
	image.SetData( img.convert('RGB').tostring() )
	return image

def process(buf, wavelet='haar', level=1):
	# custom wavelets
	if wavelet == 'haar*':
		dec_lo = [0.5, 0.5]
		dec_hi = [-0.5, 0.5]
		rec_lo = [0.5, 0.5]
		rec_hi = [0.5, -0.5]
		wavelet = pywt.Wavelet('haar*', [dec_lo, dec_hi, rec_lo, rec_hi])

	if wavelet == 'cdf9/7':
		dec_lo = [0.026748757411, -0.016864118443, -0.078223266529, 0.266864118443, 0.602949018236, 0.266864118443, -0.078223266529, -0.016864118443, 0.026748757411]
		dec_hi = [0, 0.091271763114, -0.057543526229, -0.591271763114, 1.11508705, -0.591271763114, -0.057543526229, 0.091271763114, 0]
		rec_lo = [0, -0.091271763114, -0.057543526229, 0.591271763114, 1.11508705, 0.591271763114, -0.057543526229, -0.091271763114, 0]
		rec_hi = [0.026748757411, 0.016864118443, -0.078223266529, -0.266864118443, 0.602949018236, -0.266864118443, -0.078223266529, 0.016864118443, 0.026748757411]
		wavelet = pywt.Wavelet('cdf9/7', [dec_lo, dec_hi, rec_lo, rec_hi])

	# decomposition
	subbands = pywt.wavedec2(buf, wavelet=wavelet, level=level, mode='per')

	# buffer reconstruction
	while len(subbands) is not 1:
		# trim LL
		x, y = subbands[1][0].shape
		subbands[0] = subbands[0][:x, :y]

		# concatenate LL, LH, HL, HH
		ll_lh = np.concatenate((subbands[0], subbands[1][0]), axis=1)
		hl_hh = np.concatenate((subbands[1][0], subbands[1][1]), axis=1)
		subbands = [np.concatenate((ll_lh, hl_hh), axis=0)] + list(subbands[2:])

	return subbands[0]

def save(image, path):
	# wx.Image => PIL
	img = Image.new( 'RGB', ( image.GetWidth(), image.GetHeight() ) )
	img.fromstring( image.GetData() )

	# save image
	img.save(path)
	print ' * save to %s' % path

