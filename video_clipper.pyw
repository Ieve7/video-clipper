from dearpygui.core import *
from dearpygui.simple import *
import subprocess
import os
from datetime import datetime
SCRIPT_DIR = os.path.dirname(__file__)
SAVED_THEME = os.path.join(SCRIPT_DIR, 'theme.txt')
# ==============================================================================
'''Tkinter implementation of explorer'''
from tkinter import Tk
from tkinter import filedialog
def explorer_tkinter():
	Tk().withdraw()

	opened_path  = get_value('opened_path')
	if not opened_path:
		opened_path = os.path.expanduser("~/Desktop")

	file_path = filedialog.askopenfilename(initialdir = opened_path,
											title = "Select file",
											filetypes = (	("video files",".mp4, .webm, .mkv, .gif, .flv, .vob, .ogg, .ogv, .gifv, .mng, .avi, .MTS, .M2TS, .TS, .mov, .qt, .wmv, .yuv, .rm, .mpg, .mpeg, .m2v, .m4v, .svi, .3gp, .3g2, .m4p, .mxf, .roq, .nsv, .flv, .f4v".replace(',','')),
															("all files","*.*"),
														)
											)
	dir,fn = os.path.split(file_path)
	set_value('opened_path', dir)
	set_value('opened_file', fn)

'''Function option for explorer with pure dearpygui (buggy explorer)'''
def explorer(*args):
	def cb(s,d):
		set_value('opened_file', d[1])
		set_value('opened_path', d[0])

	open_file_dialog(cb,extensions='.*, .mp4, .webm, .mkv, .gif, .flv, .vob, .ogg, .ogv, .gifv, .mng, .avi, .MTS, .M2TS, .TS, .mov, .qt, .wmv, .yuv, .rm, .mpg, .mpeg, .m2v, .m4v, .svi, .3gp, .3g2, .m4p, .mxf, .roq, .nsv, .flv, .f4v')

with window('MAIN'):
	def recall_theme():
		with open(SAVED_THEME) as f: set_theme(f.read())
	recall_theme()

	def rotate_theme(sender,caller):
		themes = '''Light, Classic, Grey, Dark Grey, Dark, Dark 2, Cherry, Purple, Gold, Red'''.split(', ')
		index = get_value('##theme')
		min = 0
		max = len(themes)-1
		if index > max:
			index = min

		if index < min:
			index = max

		set_value('##theme',index)
		with open(SAVED_THEME,'w') as f: f.write(themes[index])
		recall_theme()


	with group('file_picker',horizontal=True):

		add_button('locate video',callback=explorer_tkinter)
		add_label_text('opened_file',label='')
		add_label_text('opened_path',label='',show=False)
	add_same_line(xoffset=440)
	add_input_int('##theme',width=10,min_value=-1,default_value=0,callback=rotate_theme,tip='skin')

	add_separator()
	add_checkbox('#reference',label='long name',default_value=True,tip='reference original name in the clip\'s name?')
	add_same_line()
	add_input_text('name',width=400)

	add_separator()

	def assert_times(sender,data):
		total = lambda h,m,s: h*60*60 + m*60 + s # total seconds
		def simplify(s):
			h,m,s = 0,0,s

			if s/60 > 1:
				m += int(s/60)
				s -= int(s/60) * 60

			if m/60 > 1:
				h += int(m/60)
				m -= int(m/60) * 60

			return [h,m,s] #simplifies to h:m:s

		s = get_value('##arrow_start') if not sender == 'start' else total(*get_value('start'))
		e = get_value('##arrows_end') if not sender == 'end' else total(*get_value('end'))

		if( sender in ['start', '##arrow_start'] and s >= e ):
			e = s+1

		if( s >= e ):
			if e <= 0:
				e = 1
			s = e - 1

		in_s = simplify(s)
		in_e = simplify(e)

		set_value('start', in_s)
		set_value('end', in_e)
		set_value('##arrow_start', s)
		set_value('##arrows_end', e)

		name = get_value('name')
		if not name or '__to__' in name:
			set_value('name', '{}-{}-{}__to__{}-{}-{}'.format(*(in_s+in_e)))

	add_input_int('##arrow_start',width=10,min_value=0,default_value=0,callback=assert_times)
	add_same_line(xoffset=0)
	add_input_int3(		'start',
						min_clamped = True,
						max_clamped = True,
						max_value = 999,
						width=120,
						tip='H:M:S',
						callback=assert_times,
						on_enter=True,
					)

	add_separator()
	add_input_int('##arrows_end',width=10,min_value=1,default_value=1,callback=assert_times)
	add_same_line(xoffset=0)
	add_input_int3(		'end',
						min_clamped = True,
						max_clamped = True,
						max_value = 1000,
						width=120,
						default_value = [0,0,1],
						tip='H:M:S',
						callback=assert_times,
						on_enter=True,
					)

	add_separator()
	add_same_line(xoffset=60)

	def zero_times():
		set_value('##arrows_end',1)
		assert_times(None,'##arrows_end')

	add_button('clear', callback=zero_times)
	add_same_line(xoffset=430)
	add_listbox('format',items=['','.mp4','.gif','.webm'],width=80)
	add_separator()

	def split(*args):
		w,h = get_main_window_size()
		with window(	'this',
						width=w,         height=h,
						x_pos=0,         y_pos=0,
						no_resize=True,  no_move=True,  no_title_bar=True
		):
			add_text('status')

		in_s = get_value('start')
		in_e = get_value('end')
		in_n = get_value('name')
		if not in_n:
			in_n = '{}-{}-{}__to__{}-{}-{}'.format(*(in_s+in_e))

		start = "-ss {}:{}:{}".format(*in_s)
		end = "-to {}:{}:{}".format(*in_e)
		path = get_value('opened_path')
		if not path:
			print('no path selected')
		else:
			file = get_value('opened_file')
			ext = ['','.mp4','.gif','.webm'][get_value('format')]
			ext = (lambda a: '.'+a[len(a)-1] )(file.split('.')) if not ext else ext
			in_file = os.path.join(path,file)

			if get_value('#reference'):
				output_file = os.path.join(path, file[:len(file)-len(ext)]+f'__{in_n}__'+ext)
			else:
				output_file = os.path.join(path, f'{in_n}'+ext)

			command = f'ffmpeg -i "{in_file}" {start} {end} -y "{output_file}"'
			print(command)
			set_value('status',command)
			subprocess.Popen(command).wait()

			if get_value('open explorer'):
				command = 'explorer /select, "' + str(os.path.join(path,output_file)).replace('/','\\')+'"'

		delete_item('this')

	add_same_line(xoffset=440)
	add_button('split',callback=split)
	add_same_line(xoffset=300)
	add_checkbox('open explorer',tip='show the finished file in explorer',default_value=True)

	def youtube_dl(s,url):
		w,h = get_main_window_size()
		with window('youtube-dl',no_resize=True,no_move=True,no_close=True,no_title_bar=True, x_pos=0,y_pos=0, height=h,width=w):
			add_text('status-ytdl',default_value=url)
			print(url)
			if url:
				set_value('url','')
				set_value('status-ytdl',f'[DLing]{url}')

				name = datetime.now().strftime('%Y-%m-%d__%H-%M-%S.mp4')
				filename = os.path.expanduser("~\desktop") + '\\'+ name
				ytdl = f'youtube-dl -f best --output {filename} {url}'
				os.system(ytdl)


				set_value('opened_file',name)
				set_value('opened_path',os.path.expanduser("~\desktop"))
		delete_item('youtube-dl')

	add_separator()
	add_input_text('##notepad',multiline=True,tab_input=True,width=490,height=222)

	add_separator()
	add_text('Youtube Downloader')
	add_button('##youtube-dl',label='load url',callback=youtube_dl,callback_data=lambda *args: get_value('url'))
	add_same_line()
	add_input_text('url',width=450)

# ==============================================================================
add_additional_font('anonBlack.ttf', size=14)
set_primary_window(window='MAIN', value=True)
set_main_window_size(518,580)
set_main_window_resizable(False)
set_main_window_title('Video Clipper')
start_dearpygui()