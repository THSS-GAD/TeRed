class Graph:
	def __init__(self):
		self.node_cnt = 0
		self.edge_cnt = 0
		self.e_src = []
		self.e_dst = []
		self.e_type = []
		self.e_ts = []
		self.min_ts = -1
		self.max_ts = -1
		self.nodeId_map = {}
		self.nodeName_map = {}
		self.nodeType_map = {}
		self.W = []
		self.flag = {}
		self.in_edges = {}
		self.out_edges = {}

	def output(self):
		print('node_cnt', self.node_cnt)
		print('edge_cnt', self.edge_cnt)
		print('e_src', self.e_src)
		print('e_dst', self.e_dst)
		print('e_type', self.e_type)
		print('e_ts', self.e_ts)
		print('min_ts', self.min_ts)
		print('max_ts', self.max_ts)
		print('nodeId_map', self.nodeId_map)
		print('nodeName_map', self.nodeName_map)
		print('nodeType_map', self.nodeType_map)
		print('W', self.W)
		print('flag', self.flag)
		print('in_edges', self.in_edges)
		print('out_edges', self.out_edges)