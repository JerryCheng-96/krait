#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtSql import *

from utils import Data
from workers import SSRSearchWorker,CSSRSearchWorker
from db import FastaSSRTable

class SSRMainWindow(QMainWindow):
	def __init__(self):
		super(SSRMainWindow, self).__init__()

		self.setWindowTitle("Krait v0.0.1")
		self.setWindowIcon(QIcon(QPixmap("logo.png")))
		
		self.table = QTableView()
		self.table.verticalHeader().hide()
		self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.table.setSortingEnabled(True)
		self.table.setContextMenuPolicy(Qt.CustomContextMenu)
		self.table.doubleClicked.connect(self.showSSRSequence)
		self.model = SSRTableModel()
		self.model.refreshed.connect(self.changeRowCount)
		self.table.setModel(self.model)
		self.setCentralWidget(self.table)

		#search text input
		self.filter = QLineEdit(self)
		self.filter.setPlaceholderText("Filter data in table e.g. motif=AT and repeat>10")
		self.filter.returnPressed.connect(self.filterTable)

		#create fasta table
		self.fasta_table = FastaSSRTable()

		self.createActions()
		self.createMenus()
		self.createToolBars()
		self.createStatusBar()

		self.readSettings()

		self.show()


	def readSettings(self):
		self.settings = QSettings("config.ini", QSettings.IniFormat)
		self.resize(self.settings.value("size", QSize(900, 600)))

	def writeSettings(self):
		self.settings.setValue("size", self.size())

	def closeEvent(self, event):
		self.writeSettings()

	def createActions(self):
		#open a project action
		self.openProjectAct = QAction(self.tr("Open project"), self)
		self.openProjectAct.setShortcut(QKeySequence.Open)
		self.openProjectAct.triggered.connect(self.openProject)

		#close a project action
		self.closeProjectAct = QAction(self.tr("Close project"), self)
		self.closeProjectAct.setShortcut(QKeySequence.Close)
		self.closeProjectAct.triggered.connect(self.closeProject)
		
		#save a project action
		self.saveProjectAct = QAction(self.tr("Save project"), self)
		self.saveProjectAct.setShortcut(QKeySequence.Save)
		self.saveProjectAct.triggered.connect(self.saveProject)
		
		#save as a project action
		self.saveAsProjectAct = QAction(self.tr("Save project as..."), self)
		self.saveAsProjectAct.setShortcut(QKeySequence.SaveAs)
		self.saveAsProjectAct.triggered.connect(self.saveProjectAs)
		
		#load fasta file or genome action
		self.loadFastaAct = QAction(self.tr("Import fasta sequence"), self)
		self.loadFastaAct.triggered.connect(self.importFasta)
		self.loadFastasAct = QAction(self.tr("Import Fastas in folder"), self)
		self.loadFastasAct.triggered.connect(self.importFastas)
		
		#export the Results
		self.exportResAct = QAction(self.tr("Export Results"), self)
		
		#exit action
		self.exitAct = QAction(self.tr("Exit"), self)
		self.exitAct.setShortcut(QKeySequence.Quit)
		self.exitAct.triggered.connect(self.close)
		
		#copy action
		self.copyAct = QAction(self.tr("Copy"), self)
		self.copyAct.setShortcut(QKeySequence.Copy)
		self.copyAct.triggered.connect(self.doCopy)
		
		self.cutAct = QAction(self.tr("Cut"), self)
		self.cutAct.setShortcut(QKeySequence.Cut)
		self.cutAct.triggered.connect(self.doCut)
		
		self.pasteAct = QAction(self.tr("Paste"), self)
		self.pasteAct.setShortcut(QKeySequence.Paste)
		self.pasteAct.triggered.connect(self.doPaste)
	
		self.selectAllAct = QAction(self.tr("Select All"), self)
		self.selectAllAct.setShortcut(QKeySequence.SelectAll)
		self.selectAllAct.triggered.connect(self.doSelectAll)

		self.preferenceAct = QAction(self.tr("Preferences"), self)
		self.preferenceAct.setShortcut(QKeySequence.Preferences)
		self.preferenceAct.triggered.connect(self.setPreference)

		#toolbar actions
		#search perfect ssrs tool button
		self.perfectAct = QAction(QIcon("icons/tandem.png"), self.tr("Search SSRs"), self)
		self.perfectAct.setToolTip(self.tr("Search perfect microsatellites"))
		self.perfectAct.triggered.connect(self.searchPerfectSSRs)
		self.perfectMenuAct = QAction(self.tr("Perform SSR search"), self)
		self.perfectMenuAct.triggered.connect(self.searchPerfectSSRs)
		self.perfectResultAct = QAction(self.tr("Show perfect SSRs"), self)
		self.perfectResultAct.triggered.connect(self.showPerfectSSRs)
		self.perfectRemoveAct = QAction(self.tr("Remove perfect SSRs"), self)
		self.perfectRemoveAct.triggered.connect(self.removePerfectSSRs)
		self.minRepeatAct = QAction(self.tr("Minimum repeats"), self)
		self.minRepeatAct.triggered.connect(self.setPreference)
		
		#search compound ssrs tool button
		self.compoundAct = QAction(QIcon("icons/compound.png"), self.tr("Identify cSSRs"), self)
		self.compoundAct.setToolTip(self.tr("Identify compound microsatellites using dMax"))
		self.compoundAct.triggered.connect(self.searchCompoundSSRs)
		self.compoundMenuAct = QAction(self.tr("Perform cSSRs search"), self)
		self.compoundMenuAct.triggered.connect(self.searchCompoundSSRs)
		self.compoundResultAct = QAction(self.tr("Show compound SSRs"), self)
		self.compoundResultAct.triggered.connect(self.showCompoundSSRs)
		self.compoundRemoveAct = QAction(self.tr("Remove cSSR results"), self)
		self.compoundRemoveAct.triggered.connect(self.removeCompoundSSRs)
		self.bestDmaxAct = QAction(self.tr("Estimate best dMax"), self)
		self.bestDmaxAct.triggered.connect(self.estimateBestMaxDistance)
		self.maxDistanceAct = QAction(self.tr("Maximal allowed distance"), self)
		self.maxDistanceAct.triggered.connect(self.setPreference)

		#about action
		self.aboutAct = QAction(self.tr("About"), self)
		self.aboutAct.triggered.connect(self.about)
		

	def createMenus(self):
		self.fileMenu = self.menuBar().addMenu("&File")
		self.editMenu = self.menuBar().addMenu("&Edit")
		self.searchMenu = self.menuBar().addMenu("&Search")
		self.viewMenu = self.menuBar().addMenu("&View")
		self.toolMenu = self.menuBar().addMenu("&Tool")
		self.helpMenu = self.menuBar().addMenu("&Help")
		
		self.fileMenu.addAction(self.openProjectAct)
		self.fileMenu.addAction(self.closeProjectAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.saveProjectAct)
		self.fileMenu.addAction(self.saveAsProjectAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.loadFastaAct)
		self.fileMenu.addAction(self.loadFastasAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exportResAct)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exitAct)
		
		self.editMenu.addAction(self.copyAct)
		self.editMenu.addAction(self.cutAct)
		self.editMenu.addAction(self.pasteAct)
		self.editMenu.addSeparator()
		self.editMenu.addAction(self.selectAllAct)
		self.editMenu.addSeparator()
		self.editMenu.addAction(self.preferenceAct)

		self.searchMenu.addAction(self.perfectMenuAct)
		self.searchMenu.addAction(self.compoundMenuAct)

		self.viewMenu.addAction(self.perfectResultAct)
		self.viewMenu.addAction(self.compoundResultAct)
		self.viewMenu.addSeparator()
		self.viewMenu.addAction(self.perfectRemoveAct)
		self.viewMenu.addAction(self.compoundRemoveAct)

		self.toolMenu.addAction(self.bestDmaxAct)

		self.helpMenu.addAction(self.aboutAct)


		#tool bar menus
		#search ssrs tool button menu
		self.perfectMenu = QMenu()
		self.perfectMenu.addAction(self.perfectMenuAct)
		self.perfectMenu.addAction(self.perfectResultAct)
		self.perfectMenu.addAction(self.perfectRemoveAct)
		self.perfectMenu.addSeparator()
		self.perfectMenu.addAction(self.loadFastaAct)
		self.perfectMenu.addAction(self.loadFastasAct)
		self.perfectMenu.addSeparator()
		self.perfectMenu.addAction(self.minRepeatAct)

		self.compoundMenu = QMenu()
		self.compoundMenu.addAction(self.compoundMenuAct)
		self.compoundMenu.addAction(self.compoundResultAct)
		self.compoundMenu.addAction(self.compoundRemoveAct)
		self.compoundMenu.addSeparator()
		self.compoundMenu.addAction(self.bestDmaxAct)
		self.compoundMenu.addAction(self.maxDistanceAct)
		

	def createToolBars(self):
		self.toolBar = self.addToolBar('')
		self.toolBar.setMovable(False)
		self.toolBar.setIconSize(QSize(36, 36))
		self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

		#search ssr action and menus
		self.perfectAct.setMenu(self.perfectMenu)
		self.toolBar.addAction(self.perfectAct)

		self.compoundAct.setMenu(self.compoundMenu)
		self.toolBar.addAction(self.compoundAct)

		self.annotToolBtn = QAction(QIcon("icons/annotation.png"), self.tr("Locate SSRs"), self)
		#self.annotToolBtn.setDisabled(True)
		self.annotToolBtnMenu = QMenu()
		self.annotToolBtnMenu.addAction("Settings")
		self.annotToolBtnMenu.addAction("Testings")
		self.annotToolBtn.setMenu(self.annotToolBtnMenu)
		self.toolBar.addAction(self.annotToolBtn)

		self.statToolBtn = QAction(QIcon("icons/statistics.png"), self.tr("Analysis"), self)
		#self.statToolBtn.setDisabled(True)
		self.statToolBtnMenu = QMenu()
		self.statToolBtnMenu.addAction("Settings")
		self.statToolBtnMenu.addAction("Testings")
		self.statToolBtn.setMenu(self.statToolBtnMenu)
		self.toolBar.addAction(self.statToolBtn)

		self.reportToolBtn = QAction(QIcon("icons/report.png"), self.tr("Statistics"), self)
		#self.reportToolBtn.setDisabled(True)
		self.reportToolBtnMenu = QMenu()
		self.reportToolBtnMenu.addAction("Settings")
		self.reportToolBtnMenu.addAction("Testings")
		self.reportToolBtn.setMenu(self.reportToolBtnMenu)
		self.toolBar.addAction(self.reportToolBtn)

		#search input
		#self.filter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.toolBar.addWidget(self.filter)

	def createStatusBar(self):
		self.statusBar = self.statusBar()
		self.statusBar.showMessage("Genome-wide microsatellites analysis tool.")
		
		#add row counts widget
		self.rowCounts = QLabel("Rows: 0", self)
		self.rowCounts.setStyleSheet("margin-right:20px;")
		self.statusBar.addPermanentWidget(self.rowCounts)
		
		#add progressing bar
		self.progressBar = QProgressBar(self)
		self.statusBar.addPermanentWidget(self.progressBar)
		

	def openProject(self):
		dbfile, _ = QFileDialog.getOpenFileName(self, filter="Database (*.db)")
		if not dbfile: return
		DB.setDatabaseName(dbfile)
		DB.open()
		self.showPerfectSSRs()

	def saveProject(self):
		if not DB.databaseName():
			DB.commit()
			return

		dbfile, _ = QFileDialog.getSaveFileName(self, filter="Database (*.db)")
		if not dbfile: return
		query = QSqlQuery()
		query.exec_("ATTACH DATABASE '%s' AS 'filedb'" % dbfile)
		for table in DB.tables():
			query.exec_("CREATE TABLE filedb.%s AS SELECT * FROM %s" % (table, table))
		query.exec_("DETACH DATABASE filedb")

	def saveProjectAs(self):
		dbfile, _ = QFileDialog.getSaveFileName(self, filter="Database (*.db)")
		if not dbfile: return
		query = QSqlQuery()
		query.exec_("ATTACH DATABASE '%s' AS 'filedb'" % dbfile)
		for table in DB.tables():
			query.exec_("CREATE TABLE filedb.%s AS SELECT * FROM %s" % (table, table))
		query.exec_("DETACH DATABASE filedb")

	def closeProject(self):
		DB.close()
		del self.model
		self.model = SSRTableModel()
		self.table.setModel(self.model)
	
	def importFasta(self):
		'''
		Import a fasta file from a directory
		'''
		fasta, _ = QFileDialog.getOpenFileName(self, filter="Fasta (*.fa *.fna *.fas *.fasta);;All files (*.*)")
		if not fasta: return
		self.fasta_table.insert(Data(ID=None, path=fasta))
		self.message("Import fasta %s" % fasta)

	def importFastas(self):
		'''
		import all fasta files from a directory
		'''
		directory = QFileDialog.getExistingDirectory(self)
		if not directory: return
		folder = QDir(directory)
		count = 0
		for fasta in  folder.entryList(QDir.Files):
			self.fasta_table.insert(Data(ID=None, path=folder.absoluteFilePath(fasta)))
			count += 1
		self.message("Import %s fastas in %s" % (count, directory))

	def doCopy(self):
		focus = QApplication.focusWidget()
		if focus is 0: return
		QApplication.postEvent(focus, QKeyEvent(QEvent.KeyPress, Qt.Key_C, Qt.ControlModifier))
		QApplication.postEvent(focus, QKeyEvent(QEvent.KeyRelease, Qt.Key_C, Qt.ControlModifier))

	def doCut(self):
		focus = QApplication.focusWidget()
		if focus is 0: return
		QApplication.postEvent(focus, QKeyEvent(QEvent.KeyPress, Qt.Key_X, Qt.ControlModifier))
		QApplication.postEvent(focus, QKeyEvent(QEvent.KeyRelease, Qt.Key_X, Qt.ControlModifier))
	
	def doPaste(self):
		focus = QApplication.focusWidget()
		if focus is 0: return
		QApplication.postEvent(focus, QKeyEvent(QEvent.KeyPress, Qt.Key_V, Qt.ControlModifier))
		QApplication.postEvent(focus, QKeyEvent(QEvent.KeyRelease, Qt.Key_V, Qt.ControlModifier))
	
	def doSelectAll(self):
		focus = QApplication.focusWidget()
		if focus is 0: return
		QApplication.postEvent(focus, QKeyEvent(QEvent.KeyPress, Qt.Key_A, Qt.ControlModifier))
		QApplication.postEvent(focus, QKeyEvent(QEvent.KeyRelease, Qt.Key_A, Qt.ControlModifier))

	def setPreference(self):
		dialog = PreferenceDialog(self, self.settings)
		if dialog.exec_() == QDialog.Accepted:
			dialog.saveSettings()

	def searchPerfectSSRs(self):
		#if self.db.isTableExists('ssr'):
		#	status = QMessageBox.warning(self, 
		#		self.tr("Warning"), 
		#		self.tr("The SSRs have been searched.\nDo you want to remove result and search again?"), 
		#		QMessageBox.Ok | QMessageBox.Cancel
		#	)

		#	if status == QMessageBox.Cancel:
			
		rules = self.getMicrosatelliteRules()
		fastas = [fasta for fasta in self.fasta_table.fetchAll()]
		worker = SSRSearchWorker(self, fastas, rules)
		worker.update_message.connect(self.message)
		worker.update_progress.connect(self.setProgress)
		worker.finished.connect(self.showPerfectSSRs)
		worker.start()

	def showPerfectSSRs(self):
		self.model.setTable('ssr')
		self.table.horizontalHeader().setResizeMode(QHeaderView.Stretch)
		self.model.refresh()

	def removePerfectSSRs(self):
		pass

	def searchCompoundSSRs(self):
		dmax = int(self.settings.value('dmax', 10))
		worker = CSSRSearchWorker(self, dmax)
		worker.update_message.connect(self.message)
		worker.update_progress.connect(self.setProgress)
		worker.finished.connect(self.showCompoundSSRs)
		worker.start()

	def showCompoundSSRs(self):
		self.model.setTable('cssr')
		self.table.horizontalHeader().setResizeMode(QHeaderView.Interactive)
		self.model.refresh()

	def removeCompoundSSRs(self):
		pass

	def estimateBestMaxDistance(self):
		pass

	def filterTable(self):
		filters = str(self.filter.text())
		if filters.startswith('db'):
			self.model.setTable(filters.split('=')[1])
			self.model.select()
			return
		self.model.setFilter(filters)
		self.model.refresh()

	def showSSRSequence(self, index):
		'''
		The row in table double clicked, show the sequence of SSR
		'''
		record = self.model.record(index.row())
		flank = int(self.settings.value('flank', 50))
		
		



	def getMicrosatelliteRules(self):
		return {
			1: int(self.settings.value('mono', 12)),
			2: int(self.settings.value('di', 7)),
			3: int(self.settings.value('tri', 5)), 
			4: int(self.settings.value('tetra', 4)),
			5: int(self.settings.value('penta', 3)),
			6: int(self.settings.value('hexa', 3))
		}

	def changeRowCount(self):
		while self.model.canFetchMore():
			self.model.fetchMore()
		counts = self.model.rowCount()
		self.rowCounts.setText("Rows: %s" % counts)
		
	def setProgress(self, percent):
		self.progressBar.setValue(percent)

	def message(self, msg):
		self.statusBar.showMessage(msg)

	def about(self):
		pass

class SSRTableModel(QSqlTableModel):
	refreshed = Signal()
	def __init__(self):
		super(SSRTableModel, self).__init__()

	def refresh(self):
		self.select()
		self.refreshed.emit()


class PreferenceDialog(QDialog):
	def __init__(self, parent=None, settings=None):
		super(PreferenceDialog, self).__init__(parent)
		self.settings = settings
		self.setWindowTitle(self.tr("Preferences"))
		self.setMinimumWidth(400)

		repeatsGroup = QGroupBox(self.tr("Minimum repeats"))
		monoLabel = QLabel("Mono-nucleotide")
		self.monoValue = QSpinBox()
		diLabel = QLabel("Di-nucleotide")
		self.diValue = QSpinBox()
		triLabel = QLabel("Tri-nucleotide")
		self.triValue = QSpinBox()
		tetraLabel = QLabel("Tetra-nucleotide")
		self.tetraValue = QSpinBox()
		pentaLabel = QLabel("Penta-nucleotide")
		self.pentaValue = QSpinBox()
		hexaLabel = QLabel("Hexa-nucleotide")
		self.hexaValue = QSpinBox()
		repeatLayout = QGridLayout()
		repeatLayout.setVerticalSpacing(10)
		repeatLayout.setHorizontalSpacing(10)
		repeatLayout.setColumnStretch(1, 1)
		repeatLayout.setColumnStretch(3, 1)
		repeatLayout.addWidget(monoLabel, 0, 0)
		repeatLayout.addWidget(self.monoValue, 0, 1)
		repeatLayout.addWidget(diLabel, 0, 2)
		repeatLayout.addWidget(self.diValue, 0, 3)
		repeatLayout.addWidget(triLabel, 1, 0)
		repeatLayout.addWidget(self.triValue, 1, 1)
		repeatLayout.addWidget(tetraLabel, 1, 2)
		repeatLayout.addWidget(self.tetraValue, 1, 3)
		repeatLayout.addWidget(pentaLabel, 2, 0)
		repeatLayout.addWidget(self.pentaValue, 2, 1)
		repeatLayout.addWidget(hexaLabel, 2, 2)
		repeatLayout.addWidget(self.hexaValue, 2, 3)
		repeatsGroup.setLayout(repeatLayout)

		distanceGroup = QGroupBox(self.tr("Compound SSR maximal distance"))
		distanceLabel = QLabel("Maximal distance (dmax): ")
		self.distanceValue = QSpinBox()
		distanceLayout = QHBoxLayout()
		distanceLayout.addWidget(distanceLabel)
		distanceLayout.addWidget(self.distanceValue, 1)
		distanceGroup.setLayout(distanceLayout)

		flankGroup = QGroupBox(self.tr("Flanking sequence"))
		flankLabel = QLabel("Flanking sequence length: ")
		self.flankValue = QSpinBox()
		self.flankValue.setMaximum(1000)
		flankLayout = QHBoxLayout()
		flankLayout.addWidget(flankLabel)
		flankLayout.addWidget(self.flankValue, 1)
		flankGroup.setLayout(flankLayout)

		buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)

		spacerItem = QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

		mainLayout = QVBoxLayout()
		mainLayout.addWidget(repeatsGroup)
		mainLayout.addWidget(distanceGroup)
		mainLayout.addWidget(flankGroup)
		mainLayout.addItem(spacerItem)
		mainLayout.addWidget(buttonBox)
		self.setLayout(mainLayout)

		self.getSettings()

	def getSettings(self):
		self.monoValue.setValue(int(self.settings.value('mono', 12)))
		self.diValue.setValue(int(self.settings.value('di', 7)))
		self.triValue.setValue(int(self.settings.value('tri', 5)))
		self.tetraValue.setValue(int(self.settings.value('tetra', 4)))
		self.pentaValue.setValue(int(self.settings.value('penta', 3)))
		self.hexaValue.setValue(int(self.settings.value('hexa', 3)))
		self.distanceValue.setValue(int(self.settings.value('dmax', 10)))
		self.flankValue.setValue(int(self.settings.value('flank', 100)))


	def saveSettings(self):
		self.settings.setValue('mono', self.monoValue.value())
		self.settings.setValue('di', self.diValue.value())
		self.settings.setValue('tri', self.triValue.value())
		self.settings.setValue('tetra', self.tetraValue.value())
		self.settings.setValue('penta', self.pentaValue.value())
		self.settings.setValue('hexa', self.hexaValue.value())
		self.settings.setValue('dmax', self.distanceValue.value())
		self.settings.setValue('flank', self.flankValue.value())
		
#class SSRTableModel(QSqlTableModel):
#	def __init__(self):
#		super(SSRTableModel, self).__init__()
#		self.setTable('ssr')
#		self.select()

	#def data(self, index, role=Qt.DisplayRole):
	#	if role == Qt.TextAlignmentRole:
	#		return Qt.AlignCenter

	#	return QSqlTableModel.data(self, index, role)