import numpy as np
import cv2
from skimage.transform import estimate_transform,warp

class DlibAlign:
	#: Landmark indices corresponding to the inner eyes and bottom lip.
	INNER_EYES_AND_BOTTOM_LIP = [39, 42, 57]
	#: Landmark indices corresponding to the outer eyes and nose.
	OUTER_EYES_AND_NOSE = [36, 45, 33]
	#: Landmark indices corresponding to all point.
	ALL_POINTS = [_ for _ in range(68)]
	def __init__(self):
		TEMPLATE = np.float32([
			(0.0792396913815, 0.339223741112), (0.0829219487236, 0.456955367943),
			(0.0967927109165, 0.575648016728), (0.122141515615, 0.691921601066),
			(0.168687863544, 0.800341263616), (0.239789390707, 0.895732504778),
			(0.325662452515, 0.977068762493), (0.422318282013, 1.04329000149),
			(0.531777802068, 1.06080371126), (0.641296298053, 1.03981924107),
			(0.738105872266, 0.972268833998), (0.824444363295, 0.889624082279),
			(0.894792677532, 0.792494155836), (0.939395486253, 0.681546643421),
			(0.96111933829, 0.562238253072), (0.970579841181, 0.441758925744),
			(0.971193274221, 0.322118743967), (0.163846223133, 0.249151738053),
			(0.21780354657, 0.204255863861), (0.291299351124, 0.192367318323),
			(0.367460241458, 0.203582210627), (0.4392945113, 0.233135599851),
			(0.586445962425, 0.228141644834), (0.660152671635, 0.195923841854),
			(0.737466449096, 0.182360984545), (0.813236546239, 0.192828009114),
			(0.8707571886, 0.235293377042), (0.51534533827, 0.31863546193),
			(0.516221448289, 0.396200446263), (0.517118861835, 0.473797687758),
			(0.51816430343, 0.553157797772), (0.433701156035, 0.604054457668),
			(0.475501237769, 0.62076344024), (0.520712933176, 0.634268222208),
			(0.565874114041, 0.618796581487), (0.607054002672, 0.60157671656),
			(0.252418718401, 0.331052263829), (0.298663015648, 0.302646354002),
			(0.355749724218, 0.303020650651), (0.403718978315, 0.33867711083),
			(0.352507175597, 0.349987615384), (0.296791759886, 0.350478978225),
			(0.631326076346, 0.334136672344), (0.679073381078, 0.29645404267),
			(0.73597236153, 0.294721285802), (0.782865376271, 0.321305281656),
			(0.740312274764, 0.341849376713), (0.68499850091, 0.343734332172),
			(0.353167761422, 0.746189164237), (0.414587777921, 0.719053835073),
			(0.477677654595, 0.706835892494), (0.522732900812, 0.717092275768),
			(0.569832064287, 0.705414478982), (0.635195811927, 0.71565572516),
			(0.69951672331, 0.739419187253), (0.639447159575, 0.805236879972),
			(0.576410514055, 0.835436670169), (0.525398405766, 0.841706377792),
			(0.47641545769, 0.837505914975), (0.41379548902, 0.810045601727),
			(0.380084785646, 0.749979603086), (0.477955996282, 0.74513234612),
			(0.523389793327, 0.748924302636), (0.571057789237, 0.74332894691),
			(0.672409137852, 0.744177032192), (0.572539621444, 0.776609286626),
			(0.5240106503, 0.783370783245), (0.477561227414, 0.778476346951)])

		TPL_MIN, TPL_MAX = np.min(TEMPLATE, axis=0), np.max(TEMPLATE, axis=0)
		MINMAX_TEMPLATE = (TEMPLATE - TPL_MIN) / (TPL_MAX - TPL_MIN)
		self.TEMPLATE = TEMPLATE
		self.MINMAX_TEMPLATE = MINMAX_TEMPLATE

	def dlib_3_align(self, rgbimg, landmarks=None, img_size = 256,
	               scale = 1.0, landmarkIndices=OUTER_EYES_AND_NOSE):
		"""
		返回对齐后的图像，使用的是三个关键点对齐
		:param rgbimg: 需要对齐的图像
		:param landmarks: 检测得到的人脸的关键点
		:param img_size: 对齐后的图像尺寸
		:param scale: 图像缩放系数
		:param landmarkIndices: 对齐使用的关键点
		:return: 对齐后的人脸图像
		"""
		assert img_size is not None
		assert rgbimg is not None
		assert landmarkIndices is not None

		npLandmarks = np.float32(landmarks)
		npLandmarkIndices = np.array(landmarkIndices)

		H = cv2.getAffineTransform(npLandmarks[npLandmarkIndices],
		                           img_size * self.MINMAX_TEMPLATE[npLandmarkIndices] * scale + img_size * (1 - scale) / 2)
		thumbnail = cv2.warpAffine(rgbimg, H, (img_size, img_size))
		return thumbnail

	def dlib_68_align(self, rgbimg, landmarks=None, img_size = 256,
	               scale = 1.0, landmarkIndices=ALL_POINTS):

		assert img_size is not None
		assert rgbimg is not None
		assert landmarkIndices is not None

		npLandmarks = np.float32(landmarks)
		npLandmarkIndices = np.array(landmarkIndices)
		img_size *= scale
		tform = estimate_transform('similarity', npLandmarks[npLandmarkIndices], img_size * self.TEMPLATE[npLandmarkIndices])
		dst_img = warp(rgbimg, tform.inverse, output_shape=(img_size, img_size))
		return dst_img

def sphereface_mean_5points():
	imgSize = (112, 96)
	coord5point =np.array([[30.2946, 51.6963],[65.5318, 51.5014],
	                       [48.0252, 71.7366], [33.5493, 92.3655],
	                       [62.7299, 92.2041]])

	# imgSize = (256, 256)
	# mean_face_shape_x = [0.224152, 0.75610125, 0.490127, 0.254149, 0.726104]
	# mean_face_shape_y = [0.2119465, 0.2119465, 0.628106, 0.780233, 0.780233]

	return imgSize, coord5point
