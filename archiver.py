#!/usr/bin/env python
import argparse
import os
import subprocess

## Commandline parser
parser = argparse.ArgumentParser(description='Example: archiver.py /Volumes/SAN/Folder/ /Volumes/Archive_SAN/Folder/')
parser.add_argument('source', help='source files to be copied.')
parser.add_argument('destination', help='destination of where files should be copied to.')
parser.add_argument('-t', dest='tree', action='store_true', help='will out put a directory tree two levels deep, file count, and drops a file to cwd')
parser.add_argument('-l', dest='log', action='store_true', help='Enables logging report.')
args = parser.parse_args()


class TextColors:
	''' Attribute reference for colors, obj.name. This class sucks! '''
	green = '\033[32m'
	yellow = '\033[33m'
	blue = '\033[34m'
	red = '\033[31m'
	magenta = '\033[35m'
	cyan = '\033[36m'
	reset = '\033[0m'

class CheckPaths(self, src, dest):
	def __init__(self, p


	def check_paths(self, src, dest):
		'''Check that paths are vaild and change permissions to 777'''
		if not os.path.isdir(src):
			print ("readable_dir:{0} is not a valid path".format(src))
			print "Invalid Source"
			#raise ValueError(self, "readable_dir:{0} is not a valid path".format(prospective_dir))
		if not os.path.isdir(dest):
			print ("readable_dir:{0} is not a valid path".format(dest))
			print "Invalid Destination"
		else:

			build_chmod = "sudo chmod -R 777"  #This should be done with python
			#chmod="%s \"%s\" \"%s\"" % (build_chmod, src)
			chmod="%s \"%s\"" % (build_chmod, src)
			print chmod
			print "Changing permissions"
			subprocess.call(chmod, shell=True)
			#print "running rsync"
			self.__spawn_rsync(src, dest)


class GetSizeOf(object):
	def __init__(self, path):
		self.path = path

	def bytes_to_human(self, stats_num):
		self.stats_num = stats_num
		symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
		prefix = {}
		for i, s in enumerate(symbols):
			prefix[s] = 1 << (i+1)*10
		for s in reversed(symbols):
			if self.stats_num >= prefix[s]:
				value = float(self.stats_num) / prefix[s]
				return '%.1f%s' % (value, s)
		return "%sB" % self.path

	def	get_size(self):
		#print self.path
		total_size = os.path.getsize(self.path)
		for item in os.listdir(self.path):
			itempath = os.path.join(self.path, item)
			if os.path.isfile(itempath):
				total_size += os.path.getsize(itempath)
			elif os.path.isdir(itempath):
				#print(itempath)
				total_size += GetSizeOf(itempath).get_size()
		self.bytes_to_human(total_size)
		return total_size

#class cvcpSync(subprocess.Popen):
#	def __init__(self, src, dest):
#		self.src

class rsyncWrap(subprocess.Popen):
#class rsyncWrap(subprocess.call):
	def __init__(self, src, dest):
		self.src = src
		self.dest = dest
		self.colors = TextColors()
		#print self.src
		#print self.dest
		return

	def __reporting(self, path):
		''' Turn reporting method into its own class. '''
		#print path
		num_files = sum([len(files) for r, d, files in os.walk(path)])
		#num_files = len([files for files in os.listdir(path) if os.path.isfile(os.path.join(path, files))])
		#print "number of files in %s %s" % (path, num_files)
		size_of = GetSizeOf(path)
		statsreport = size_of.get_size()
		total_size = size_of.bytes_to_human(statsreport)
		print self.colors.green+"Path: %s" % (path)
		print self.colors.green+"Nubmer of Files: ", num_files
		print "Total Size: ", total_size+self.colors.reset, "\n"
		#print read_size
		return num_files

	def file_count(self,src, dest):
		#This function needs to be redone.
		src_base_name = os.path.basename(os.path.normpath(src))
		dest_path = dest+'/'+src_base_name
		self.__reporting(src)
		self.__reporting(dest_path)

	def __spawn_rsync(self, src, dest):
		#Build the rsync command
		#print self.src, self.dest
		rsync = "rsync"  #might need to switch over to os.copy
		arguments = "-ruvWP"
		cmd = "%s %s \"%s\" \"%s\"" % (rsync, arguments, src, dest)
		#print cmd
		#Spawn the rsync process. Need to raise an error if rsync fails
		print "Starting Rsync Job"
		#super(rsyncWrap,self).__init__(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		print cmd
		subprocess.call(cmd, shell=True)
		self.file_count(src, dest)

	def check_paths(self, src, dest):
		'''Check that paths are vaild and change permissions to 777'''
		if not os.path.isdir(src):
			print ("readable_dir:{0} is not a valid path".format(src))
			print "Invalid Source"
			#raise ValueError(self, "readable_dir:{0} is not a valid path".format(prospective_dir))
		if not os.path.isdir(dest):
			print ("readable_dir:{0} is not a valid path".format(dest))
			print "Invalid Destination"
		else:

			build_chmod = "sudo chmod -R 777"  #This should be done with python
			#chmod="%s \"%s\" \"%s\"" % (build_chmod, src)
			chmod="%s \"%s\"" % (build_chmod, src)
			print chmod
			print "Changing permissions"
			subprocess.call(chmod, shell=True)
			#print "running rsync"
			self.__spawn_rsync(src, dest)



if __name__ == "__main__":

	rsync=rsyncWrap(args.source,args.destination)
	rsync.check_paths(args.source, args.destination)
