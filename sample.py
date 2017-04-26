from collections import namedtuple
import datetime
import pprint
import sys
import ProjectManager


def DaysPerMonth(m):
	return 30 * m

def toDate(s):
	if s=="":
		return None
	return datetime.date(int(s[0:4]), int(s[5:7]), int(s[8:10]))



#################################

"""
Project
	title:
		プロジェクト名
	url:
		プロジェクトページ
	owner:
		主担当
		[裏技] 通常同じ名前の人は同時に 1 つのことしかできないが, 数字付きの名前にして開始日を設定すると 2 つ以上にできる.
	status:
		"" : 未着手
		"o" : 作業中
		"v" : 完了
	days:
		完了までの想定作業日数
	startDate:
		着手開始日
		"" | "yyyy-mm-dd"
	doc:
		メモ
"""
projects = [
	ProjectManager.Project(
		codeName  = "BKK",
		title     = "バンコク旅行",
		url       = "",
		owner     = "Foo",
		priority  = 1,
		status    = {
			"Lab":               "o",
			"Req":               "o",
			"Design":            "o",
			"ImplDev":           "",
			"ImplProduction":    "",
			"DeployProduction":  "",
			"End":               "",
		},
		days      = DaysPerMonth(2),
		startDate = toDate(""),
		endDate   = toDate(""),
		doc       = "",
	),

	ProjectManager.Project(
		codeName  = "SING",
		title     = "シンガポール旅行",
		url       = "",
		owner     = "Foo",
		priority  = 2,
		status    = {
			"Lab":               "o",
			"Req":               "o",
			"Design":            "o",
			"ImplDev":           "",
			"ImplProduction":    "",
			"DeployProduction":  "",
			"End":               "",
		},
		days      = DaysPerMonth(1),
		startDate = toDate(""),
		endDate   = toDate(""),
		doc       = "",
	),

	ProjectManager.Project(
		codeName  = "HK",
		title     = "香港旅行",
		url       = "",
		owner     = "",
		priority  = 3,
		status    = {
			"Lab":               "v",
			"Req":               "v",
			"Design":            "o",
			"ImplDev":           "o",
			"ImplProduction":    "o",
			"DeployProduction":  "",
			"End":               "",
		},
		days      = DaysPerMonth(4),
		startDate = toDate("2017-04-01"),
		endDate   = toDate(""),
		doc       = "",
	),


	ProjectManager.Project(
		codeName  = "BKK2",
		title     = "バンコク旅行",
		url       = "",
		owner     = "Bar",
		priority  = 3.4,
		status    = {
			"Lab":               "v",
			"Req":               "v",
			"Design":            "o",
			"ImplDev":           "o",
			"ImplProduction":    "o",
			"DeployProduction":  "",
			"End":               "",
		},
		days      = DaysPerMonth(2),
		startDate = toDate(""),
		endDate   = toDate(""),
		doc       = "",
	),

]

css = """
.grad {
	background: linear-gradient(to bottom, rgba(62,140,72,1) 0%,rgba(68,148,80,1) 50%,rgba(43,119,54,1) 51%,rgba(34,112,44,1) 100%);
}
"""

project_list_header = """
<h1 class="grad">プロジェクト一覧</h1>
<ul>
<li> (ただし書きとかはここに書く)
</ul>
"""

schedule_header = """
<h1 class="grad">開発スケジュール</h1>
<ul>
<li> (ただし書きとかはここに書く)
</ul>
"""

people = "Alice".split()
status_master = [
	("Lab", "原理検討"),
	("Req", "関係者との要件合意"),
	("Design", "設計"),
	("ImplDev", "dev向け実装"),
	("ImplProduction", "本番環境向け実装"),
	("DeployProduction", "本番投入"),
	("End", "完了"),
]
# プロジェクト一覧, スケジュールが含まれる sample.html を生成する
filename = "sample.html"
ProjectManager.run(projects, people, status_master, css, project_list_header, schedule_header, filename)

