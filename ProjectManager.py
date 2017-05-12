from collections import namedtuple
import datetime
import pprint
import sys
import copy

def expandStatusValue(v):
	"""
	v : string | (string, datetime.date | None)
	が string だった場合 (string, None) に展開する.
	"""
	if isinstance(v, str):
		v = (v, None)
	return v

def formatDate(d):
	if not d:
		return "????-??-??"
	return "{0:%Y-%m-%d}".format(d)

"""
title:
	プロジェクト名
url:
	プロジェクトページ
owner:
	主担当
status:
	"" : 未着手
	"o" : 作業中
	"v" : 完了
days:
	完了までの想定作業日数
startDate:
	着手開始日
	"" | "yyyy-mm-dd"
blocking:
	着手できない理由
doc:
	メモ
milestones:
	(finishDate : datetime.date | None, title : string)[]
"""
class Project:
	def __init__(self, codeName="", title="", url="", owner="", priority=100, status={}, days=0,
		startDate=None, endDate=None, blocking="", doc="", milestones=[], epic=""):
		self.index = 0
		self.codeName = codeName
		self.title = title
		self.url = url
		self.owner = owner
		self.orig_owner = owner
		self.priority = priority
		self.status = dict([(k, expandStatusValue(v)) for k, v in status.items()])
#		pprint.pprint(self.status)
		self.days = days
		self.startDate = startDate
		self.endDate = endDate
		self.doc = doc
		self.blocking = blocking
		self.put = False
		self.milestones = milestones
		self.epic = epic

	def isDone(self):
		return self.status["End"][0]=="v"

	def doing(self):
		sd = self.startDate
		if sd is None:
			sd = datetime.date(3000, 1, 1)
		ed = self.endDate
		if ed is None:
			ed = datetime.date(3000, 1, 1)
		now = datetime.date.today()
		return sd <= now and now <= ed

	def fixed(self):
		return self.owner != "" and self.startDate is not None and self.endDate is not None

	def getMilestones(self, status_master):
		"""
		return (datetime.date, label)[]
		"""
		sm = dict(status_master)
		rv = [ (v[1], self.title+" "+sm[k]+" (主担当: "+self.owner+")") for k, v in self.status.items() ] + self.milestones
		return list(filter(lambda v: v[0], rv))

colorDone = "#DDFADE"
colorDoing = "#E0F0FF"

def hsv2rgb(hsv):
	"""
	hsv: [h, s, v]
		h in [0, 360]
		s in [0, 1]
		v in [0, 1]
	return [r, g, b]
		r, g, b in [0, 1]
	"""
	h = hsv[0]
	s = hsv[1]
	v = hsv[2]
	hd = h/60; # in [0, 6]
	r = v
	g = v
	b = v
	if s > 0:
		hdi = max(0, min(5, int(hd)));
		f = hd - hdi
		if hdi==0:
			g *= 1 - s * (1-f)
			b *= 1 - s
		elif hdi==1:
			r *= 1 - s * f
			b *= 1 - s
		elif hdi==2:
			r *= 1 - s
			b *= 1 - s * (1-f)
		elif hdi==3:
			r *= 1 - s
			g *= 1 - s * f
		elif hdi==4:
			r *= 1 - s * (1-f)
			g *= 1 - s
		elif hdi==5:
			g *= 1 - s
			b *= 1 - s * f
	return [r, g, b]

def rgb2hex(rgb):
	return "#%02x%02x%02x" % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))



def statusCell(st, name, label):
	s, endDate = st[name]
	col = ""
	if s=="v":
		col = colorDone
	if s=="o":
		col = colorDoing
	style=""
	if col:
		style = "background-color: {col};".format(**vars())
	text = " "
	if endDate:
		text = "<span style='font-size: 0.7em;'>{endDate.year:04}-{endDate.month:02}-{endDate.day:02}</span>".format(**vars())
	return """<td style="{style}">{text}</td>""".format(**vars())

def genProjectListHtml(projects, status_master, ticketLinkFun):

	### Generate milestone list
	milestones = sorted(sum([ p.getMilestones(status_master) for p in projects], []))
	s = "\n".join([ "<li>"+formatDate(d)+" "+s+"</li><br>" for d, s in milestones if datetime.date.today() <= d])
	html = """
<ul>
<li>今後のマイルストーン一覧</li>
<ul>
{s}
</ul>
</ul>
	""".format(**vars())

	### Generate project list
	def sortFun(v):
		return v.priority + (1000 if v.isDone() else 0) + (500 if v.blocking else 0)
	projects = sorted(projects, key=sortFun)

	statusTitles = "".join([ """<td style="width: 5%;">{label}</td>""".format(**vars()) for name, label in status_master])
	html += """
<html><body><table class="projects">
<tr class="title">
	<td style="width: 5%;">番号</td>
	<td style="width: 5%;">優先度</td>
	<td>プロジェクト名</td>
	{statusTitles}
	<td style="width: 5%;">主担当</td>
	<td style="width: 10%;">メモ</td>
	<td style="width: 10%;">作業期間(予定)</td>
</tr>
""".format(**vars())

	for i, p in enumerate(projects):
		if p.startDate:
			startS = "{0:%Y-%m-%d}".format(p.startDate)
			endS = "{0:%Y-%m-%d}".format(p.endDate)
		else:
			startS = "未定"
			endS = "{p.days}日間".format(**vars())
		schedule = "{startS}<br>〜{endS}".format(**vars())
		if p.isDone():
			schedule = ""
		title = p.title
		if p.url:
			title = """<a href="{p.url}">{title}</a>""".format(**vars())
#		status = StatusDetail(p.status)
		statusTitles = "".join([ statusCell(p.status, name, label) for name, label in status_master])
		trCol = "white" if i%2==0 else "#f0f0f0"
		schedule_bg = "background-color: "+colorDoing+";" if p.doing() else ""
		index = i+1
		owner_note = ""
		doc_note = ""
		if p.orig_owner=="":
			owner_note = "(仮)"
			doc_note = "(TODO 主担当決め)"
		tasks = ""
		if p.epic:
			link = ticketLinkFun(p.epic)
			style = """background-color: darkgreen; color: white; text-decoration: none; font-size: 0.8em; padding: 4px; border-radius: 10px;"""
			tasks = """<a href="{link}" target="_blank" style="{style}">Tasks</a>""".format(**vars())
		html += """
<tr style="background-color: {trCol}">
	<td>{index}</td>
	<td>{p.priority}</td>
	<td><span style="font-size: 0.8em; font-weight: bold; color: #5050c0;">{p.codeName}</span> {tasks}<br>{title}</td>
	{statusTitles}
	<td>{p.owner}{owner_note}</td>
	<td>{p.doc}{doc_note}<span style="color: red;">{p.blocking}</span></td>
	<td style="font-size: 0.5em;{schedule_bg}">{schedule}</td>
</tr>
""".format(**vars())
	html += """
</table></body></html>
"""
	return html

def Xsect(p0, p1):
#	return Xsect(p0.startDate, p0.endDate, p1.startDate, p1.endDate)
	if any([ v is None for v in [p0.startDate, p0.endDate, p1.startDate, p1.endDate]]):
		return False
	return not (p1.endDate < p0.startDate or p0.endDate < p1.startDate)

#def Xsect(s0, e0, s1, e1):
#	return not (e1 < s0 or e0 < s1)

def dupCheck(p, projects):
	"""
	重複してなければ True を返す.
	"""
	if p.isDone():
		return True
	if not p.fixed():
		return True
	for pp in projects:
		if pp.fixed() and not pp.isDone() and p.owner==pp.owner and p.title != pp.title:
			if Xsect(p, pp):
				print("[CONFLICT]", p.title, p.startDate, p.endDate, p.owner, "AND", pp.title, pp.startDate, pp.endDate, pp.owner)
				return False
	return True

def isClone(name):
	"""
	クローンかどうか.
	クローンには明示的なプロジェクト割り当てしかできない.
	"""
	return any([str(i) in name for i in range(10)])

def assign(projects, people):
	# 担当者に割り当てた上で各PJがいつ終わるかというスケジュール表(担当者 x PJの表)
	# TODO startDate がきまってるやつを最初に置く
	# 担当者 -> 着手可能日付
	freeDates = dict([(p, datetime.date.min) for p, _ in people])
	# owner -> {startDate, project}[]
	schedule = {}
	"""
	startDateFixed
		開始日がきまってるやつを置く
	canStart
		開始日がきまってないやつを置く
	blocking
		開始できないやつを置く
	"""
	for phase in ["startDateFixed", "canStart", "blocking"]:
		print("\nPhase", phase, "\n")
		if phase=="canStart":
			for k in freeDates:
				freeDates[k] = max(freeDates[k], datetime.date.today())
		for p in sorted(projects, key=lambda v: (v.priority, v.title)):
			if phase!="blocking" and p.blocking:
				continue
			if phase=="startDateFixed" and p.startDate is None:
				continue
			if p.isDone():
				continue
			if p.put:
				continue

			print("Try to put", p.title)

			def filterFun(name):
				pp = copy.deepcopy(p)
				pp.owner = name
				return dupCheck(pp, projects)
			def getFreePerson(freeDates):
				cands = sorted([ kv for kv in freeDates.items() if not isClone(kv[0]) and filterFun(kv[0]) ], key=lambda v: (v[1], v[0]))
				print(cands)
				return cands[0][0]

			person = p.owner
			if person=="":
				person = getFreePerson(freeDates)

		#	print(person)
			origStartDate = p.startDate
			origEndDate = p.endDate
			if p.blocking:
				# Later
				p.startDate = datetime.date.today() + datetime.timedelta(365*3)
			if p.startDate is None:
				p.startDate = freeDates[person]
			if p.endDate is None:
				p.endDate = p.startDate + datetime.timedelta(p.days)

			if not dupCheck(p, projects):
				p.startDate = origStartDate
				p.endDate = origEndDate
#				continue
				sys.exit(0)

			schedule.setdefault(person, [])
			p.owner = person
			print("Put", p.title, p.startDate, p.endDate, person)
			schedule[person].append(p)
			p.put = True
			freeDates[person] = max(freeDates[person], p.endDate + datetime.timedelta(1))
	#pprint.pprint(freeDates)
#	pprint.pprint(schedule)
#	for p in projects:
#		print("[]", p.title, p.startDate, p.endDate)

	for p in projects:
		if not p.isDone():
			for pp in projects:
				if not pp.isDone() and p.title != pp.title and p.owner==pp.owner and p.title < pp.title:
					if Xsect(p, pp):
						print("[CONFLICT]", p.title, p.startDate, p.endDate, p.owner, "AND", pp.title, pp.startDate, pp.endDate, pp.owner)
	return schedule

def genScheduleHtml(projects, schedule, people, ticketLinkFun):
	# date x 担当者
	allDates = [ d for ps in schedule.values() for p in ps for d in [p.startDate, p.endDate]]
	minDate = min(allDates)
	maxDate = max(allDates)

	colors = [ rgb2hex(hsv2rgb([i/len(projects)*360, 0.1, 1])) for i in range(len(projects)) ]

	startDateIndex = minDate.toordinal()
	endDateIndex = maxDate.toordinal()
	N = endDateIndex - startDateIndex + 1

#	print(N)

	def createRow():
		return [ ["", ""] for _ in range(len(people)+1) ]

	table = {0: createRow()}

	# 定期
	for i in range(10000):
		d = minDate + datetime.timedelta(i)
		if maxDate < d:
			break
		if d.day in [1, 15, 30]:
			table.setdefault(d.toordinal(), createRow())

	wp = 95/len(people)

	# プロジェクト設置
	for i, (person, ps) in enumerate(sorted(schedule.items())):
		for p in ps:
#			print(p.startDate, p.endDate)
			si = p.startDate.toordinal()
			ei = p.endDate.toordinal()
			for d in [si, ei]:
				table.setdefault(d, createRow())
				if d==si:
					title = p.title
					if p.url:
						title = """
<a href="{p.url}">{title}</a>
""".format(**vars())
					title += "<br>"
					doc = p.doc.replace("\n", "<br>")
					title += """
					<span style="font-size: 0.8em;">{doc}</span>""".format(**vars())
					title += """<br><span style="color: red;">{p.blocking}</span>""".format(**vars())
					table[d][i+1][0] = title
					table[d][i+1][1] = "font-size: 1em;"

	# 色塗り
	for i, (person, ps) in enumerate(sorted(schedule.items())):
		for p in ps:
			si = p.startDate.toordinal()
			ei = p.endDate.toordinal()
			for d in sorted(table.keys()):
				if si <= d and d <= ei:
					col = colors[p.index]
					table[d][i+1][1] += "width: {wp}%; background-color: {col};".format(**vars())

	# 日付
	today = datetime.date.today()
	for d in table:
		if d==0:
			continue
		da = datetime.date.fromordinal(d)
		s = "{0:%Y-%m-%d}".format(da)
		col = "white" if da.month % 2==0 else "#e0e0e0"
		if da.year==today.year and da.month==today.month:
			col = "#c0ffff"
		style = "vertical-align: top; width: 5%; font-size: 3px; background-color: "+col+";"
		table[d][0] = [s, style]

	table = [ table[k] for k in sorted(table.keys()) ]
#	pprint.pprint(table)

	def createHeader():
		"""
		メンバー見出しを生成
		"""
		row = [["", ""]]
		for i, (person, ps) in enumerate(sorted(schedule.items())):
			row.append([person, "width: %f; background-color: #e0e0e0".format(**vars())])
		return row

	for i in range(0, len(table), 10):
		table.insert(i, createHeader())

	def tableToHtml(table):
		html = "<table class='schedule'>"
		for row in table:
			html += "<tr>"
			for text, style in row:
				html += "<td style='{style}'>{text}</td>".format(**vars())
			html += "</tr>"
		html += "</table>"
		return html

	return tableToHtml(table)


######################

def createTasksHtml(titleAndEpics, members, ticketLinkFun):
	def entry(label, url):
		return """<a href="{url}" target="main_frame">{label}</a>""".format(**vars())

	epics = [ epic for _, epic in titleAndEpics ]
	epicHtml = "　".join([ entry(title, ticketLinkFun(epic)) for title, epic in titleAndEpics ])
	memberHtml = "　".join([ entry(name, ticketLinkFun("", name)) for name in members ])
	memberNotInEpicsHtml = "　".join([ entry(name, ticketLinkFun("", name, "", epics)) for name in members ])
	notInEpicsHtml = entry("管理Epicに関連付けられてないチケット", ticketLinkFun("", "", "", epics))

	html = """
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1, user-scalable=no">
</head>
<frameset rows="100px,*" frameborder=1 border=1>
	<frame name="menu_frame" src="menu.html">
	<frame name="main_frame" src="">
</frameset>
</html>
""".format(**vars())

	filename = "tasks.html"
	with open(filename, "w") as f:
		print(html, file=f)
	print("[ProjectManager.createTasksHtml] OK. Wrote", filename)

	html = """
<html>
<head>
<meta charset="UTF-8">
</head>
<body style="margin: 0; font-size: 0.7em;">
Projects : {epicHtml}<br>
Members : {memberHtml}<br>
Members (管理Epicに関連付けられてないチケット): {memberNotInEpicsHtml}<br>
{notInEpicsHtml}<br>
</body>
</html>

""".format(**vars())

	filename = "menu.html"
	with open(filename, "w") as f:
		print(html, file=f)
	print("[ProjectManager.createTasksHtml] OK. Wrote", filename)

######################



def run(projects, people, status_master, ticketLinkFun, css="", project_list_header="", schedule_header="",
	statusFilename="status.html",
	tasksFilename="tasks.html"):

	"""
	people:
		(Name, NameInTicketSystem)[]
	ticketLinkFun:
		epic : string, assignee : string, label : string -> url : string
	"""
	codeNames = {}
	for p in projects:
		codeNames.setdefault(p.codeName, 0)
		codeNames[p.codeName] += 1
	bad = False
	for k, v in codeNames.items():
		if 1 < v:
			print("[ERROR] Duplicate code name:", k, "(", v, "projects)")
			bad = True
	if bad:
		print()
		return
	
	for i, p in enumerate(projects):
		p.index = i
		names = [ name for name, _ in people ]
		if p.owner and p.owner not in names:
			people.append((p.owner, ""))
	people = list(set(people))

	schedule = assign(projects, people)

	projectsHtml = genProjectListHtml(projects, status_master, ticketLinkFun)
	scheduleHtml = genScheduleHtml(projects, schedule, people, ticketLinkFun)

	css = """
body {
	margin: 0;
}
h1 {
	font-size: 1.2em;
	background-color: darkgreen;
	color: white;
	padding: 10px;
}
table {
	border-spacing: 1;
	margin-left: 20px;
}
table.projects tr.title td {
	color: white;
	padding: 5px;
}
table.projects tr.title {
	background-color: darkgreen;
}
table.example tr td {
	margin: 20px;
	font-size: 0.9em;
}
table.schedule {
	border-spacing: 0;
}
table.schedule tr td {
	padding: 0;
}
""" + css

	example = """
<table class="example"><tr>
	<td style="background-color: white;">未着手</td>
	<td style="background-color: {colorDoing};">作業中</td>
	<td style="background-color: {colorDone};">完了</td>
</tr></table>
""".format(**globals())

	html = """
<html>
<head>
<meta charset="utf-8" />
<style>
{css}
</style>
</head>
<body>

{project_list_header}

<br><br>
{example}
<br><br>

{projectsHtml}

<br><br>

{schedule_header}

{scheduleHtml}

<hr>
<a href="https://github.com/kojingharang/ManagerKit/blob/master/ProjectManager.py">Source</a>

</body>
</html>
""".format(**vars())

	with open(statusFilename, "w") as f:
		print(html, file=f)
	print("[ProjectManager.run] OK. Wrote", statusFilename)

	titleAndEpics = [(p.title, p.epic) for p in sorted(projects, key=lambda p: p.priority) if p.epic and not p.isDone()]
	members = [ name for _, name in people if name]
	createTasksHtml(titleAndEpics, members, ticketLinkFun)







