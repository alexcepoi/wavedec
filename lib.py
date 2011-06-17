import wx
import Image

def transform(image, wavelet='haar', level=1):
	# wx.Image => PIL
	img = Image.new( 'RGB', ( image.GetWidth(), image.GetHeight() ) )
	img.fromstring( image.GetData() )

	# process
	print ' * transform with <%s> level %d' % (wavelet, level)

	# PIL => wx.Image
	image = wx.EmptyImage( img.size[0], img.size[1] )
	image.SetData( img.convert('RGB').tostring() )
	return image.Blur(level * 2)

def save(image, path):
	print ' * save to %s' % path

