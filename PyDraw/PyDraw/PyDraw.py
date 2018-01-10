
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLabel, QFrame, QPushButton, QFileDialog
from PyQt5.QtGui import QPainter, QPixmap, QImage, QPen
from PyQt5.QtCore import Qt, QPoint
import sys
import random

class Button(QPushButton):  
	def __init__(self, title, parent):
		super().__init__(title, parent)

class View(QWidget):
	def __init__(self, parent):
		super().__init__(parent)
		self.setMouseTracking(True)		
		self.x = 0
		self.y = 0
		self.prevX = 0
		self.prevY = 0
		
		self.viewSize = 512
		self.brushSize = 3
		self.isSmoothDrawing = True

		self.buffer = QImage(self.viewSize, self.viewSize, QImage.Format_ARGB32)		
		self.buffer.fill(Qt.white)
		self.undoBuffer = self.buffer.copy()
		self.guide = self.buffer.copy()
		
		self.setMinimumSize(self.viewSize,self.viewSize)
		self.setMaximumSize(self.viewSize,self.viewSize)
		
	def paintEvent(self, e):
		qp = QPainter()
		qp.begin(self)
		
		# Draw sketch
		qp.setOpacity(1.0)
		qp.drawImage(0,0,self.buffer)
		
		# Draw guide
		guide_rect = self.guide.rect()
		guide_rect.moveCenter(self.buffer.rect().center())
		qp.setOpacity(0.1)
		qp.drawImage(guide_rect,self.guide)

		# Overlay other sketch
		qp.setOpacity(0.1)
		qp.drawImage(0,0,self.otherView.buffer)

		# Overlay a grid
		numSteps = 16
		stepSize = self.viewSize / numSteps

		qp.setOpacity(0.1)
		pen = QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
		qp.setPen(pen)

		for i in range(numSteps):
			qp.drawLine(0, (i + 1) * stepSize, self.viewSize, (i + 1) * stepSize)
			qp.drawLine((i + 1) * stepSize, 0, (i + 1) * stepSize,  self.viewSize)
			
		pen = QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
		qp.setPen(pen)
		qp.drawLine(self.viewSize / 2.0, 0, self.viewSize / 2.0,  self.viewSize)
		qp.drawLine(0, self.viewSize / 2.0, self.viewSize, self.viewSize / 2.0)

		qp.end()
		
	def mousePressEvent(self, e):
		self.x = self.prevX = e.x()
		self.y = self.prevY = e.y()

		self.setFocus()

		if e.button() == Qt.LeftButton:
			self.undoBuffer = self.buffer.copy()

	def mouseReleaseEvent(self, e):
		if e.button() == Qt.RightButton:
			self.buffer = self.undoBuffer.copy()
			self.update()
			self.otherView.update()

	def mouseMoveEvent(self, e):
		self.x = e.x()
		self.y = e.y()

		if e.buttons() == Qt.LeftButton:
			print('x ' + str(self.x))
			qp = QPainter()
			qp.begin(self.buffer)
			if self.isSmoothDrawing:
				qp.setRenderHint(QPainter.Antialiasing)
			pen = QPen(Qt.black, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
			qp.setPen(pen)
			qp.drawLine(self.prevX, self.prevY, self.x, self.y)
			qp.end()

			self.update()
			self.otherView.update()

		self.prevX = self.x
		self.prevY = self.y

	def keyPressEvent(self, event):
		print ("Loading image...")
		if event.key() == Qt.Key_Space:			
			fileName = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")			
			self.guide.load(fileName[0])
			self.update()
		if event.key() == Qt.Key_L:	
			img = self.buffer.copy()
			fileName = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")		
			img.load(fileName[0])
			self.buffer.fill(Qt.white)

			qp = QPainter()
			qp.begin(self.buffer)
			irect = img.rect()
			irect.moveCenter(self.buffer.rect().center())
			qp.drawImage(irect, img)
			qp.end()
			self.update()

		event.accept()


class Example(QWidget):
	
	def __init__(self):
		super().__init__()		
		self.initUI()
		
		
	def initUI(self):      
		grid = QGridLayout()
		grid.setSpacing(10)
		
		x = 0
		y = 0
		self.text = "x: {0},  y: {1}".format(x, y)	
		
		# Add mouse coordinates label
		self.label = QLabel(self.text, self)
		grid.addWidget(self.label, 0, 0, Qt.AlignTop)

		# Add left view
		view1 = View(self)
		grid.addWidget(view1, 1, 0)
		self.view1 = view1
		
		# Add right view
		view2 = View(self)
		grid.addWidget(view2, 1, 1)		
		self.view2 = view2
		
		self.view1.otherView = view2
		self.view2.otherView = view1
		
		# Clear button
		clearButton1 = Button('Clear', self)
		clearButton2 = Button('Clear', self)
		clearButton1.clicked.connect(self.clearButton1Clicked)  
		clearButton2.clicked.connect(self.clearButton2Clicked)  
		grid.addWidget(clearButton1, 2, 0)
		grid.addWidget(clearButton2, 2, 1)
		
		# Symmetry button
		symmetryButton = Button('Symmetric..', self)
		symmetryButton.clicked.connect(self.symmetryButtonClicked)   
		grid.addWidget(symmetryButton, 3, 0)
		
		# Save button
		saveButton = Button('Save...', self)
		saveButton.clicked.connect(self.saveButtonClicked)   
		grid.addWidget(saveButton, 3, 1)   

		self.setMouseTracking(True)		
		self.setLayout(grid)		
		self.setGeometry(300, 300, 350, 200)
		self.setWindowTitle('PyDraw')
		self.show()
		
	def clearButton1Clicked(self):
		self.view1.buffer.fill(Qt.white)
		self.view1.update()
		self.view2.update()
		
	def clearButton2Clicked(self):
		self.view2.buffer.fill(Qt.white)
		self.view1.update()
		self.view2.update()

	def saveButtonClicked(self):		
		print("Saving Views..")
		self.view1.buffer.save('view1.png')
		self.view2.buffer.save('view2.png')
		print("Done.")

	def symmetryButtonClicked(self):
		print('Apply symmetry.')

		flippedCopy = self.view1.buffer.copy()
		fqp = QPainter()
		fqp.begin(flippedCopy)
		transf = fqp.transform()
		transf.scale(-1, 1)
		fqp.setTransform(transf)
		fqp.drawImage(-self.view1.viewSize,0,self.view1.buffer,0,0,self.view1.viewSize * 0.5,self.view1.viewSize)
		fqp.end()

		self.view1.buffer = flippedCopy.copy()

		#qp = QPainter()
		#qp.begin(self.view1.buffer)
		#
		#qp.end()
		
		self.view1.update()
		self.view2.update()

	def mouseMoveEvent(self, e):
		x = e.x()
		y = e.y()
		
		text = "x: {0},  y: {1}".format(x, y)
		self.label.setText(text)

if __name__ == '__main__':
	
	app = QApplication(sys.argv)
	ex = Example()
	sys.exit(app.exec_())