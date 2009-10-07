#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

import PyQt4.Qwt5 as Qwt
from PyQt4 import QtCore
from audiodata import *

class FreqScaleDraw(Qwt.QwtScaleDraw):
	def __init__(self, *args):
		Qwt.QwtScaleDraw.__init__(self, *args)

	def label(self, value):
		if value >= 1e3:
			label = "%dk" %(value/1e3)
		else:
			label = "%d" %(value)
		return Qwt.QwtText(label)

class PlotImage(Qwt.QwtPlotItem):

	def __init__(self):
		pass
		Qwt.QwtPlotItem.__init__(self)

		self.parent_plot = None

		#self.rawspectrogram = RawSpectrogram()
		#self.freqscaledspectrogram = FreqScaledSpectrogram()
		self.canvasscaledspectrogram = CanvasScaledSpectrogram()

	def addData(self, xyzs, logfreqscale):
		#self.rawspectrogram.addData(xyzs)
		#self.freqscaledspectrogram.addData(xyzs, logfreqscale)
		self.canvasscaledspectrogram.setlogfreqscale(logfreqscale)
		self.canvasscaledspectrogram.addData(xyzs)

	def draw(self, painter, xMap, yMap, rect):
		#pass
		self.canvasscaledspectrogram.setcanvas_vsize(rect.height())
		self.canvasscaledspectrogram.setcanvas_hsize(rect.width())

		pixmap = self.canvasscaledspectrogram.getpixmap()
		offset = self.canvasscaledspectrogram.getpixmapoffset()
		painter.drawPixmap(rect.left(), rect.top(), pixmap,  offset,  0,  0,  0)

	def erase(self):
		#pass
		# set the data array to zero
		#self.rawspectrogram.erase()
		#self.freqscaledspectrogram.erase()
		self.canvasscaledspectrogram.erase()

class ImagePlot(Qwt.QwtPlot):

	def __init__(self, *args):
		Qwt.QwtPlot.__init__(self, *args)

		# we do not need caching
		self.canvas().setPaintAttribute(Qwt.QwtPlotCanvas.PaintCached, False)
		self.canvas().setPaintAttribute(Qwt.QwtPlotCanvas.PaintPacked, False)

		# set plot layout
		self.plotLayout().setMargin(0)
		self.plotLayout().setCanvasMargin(0)
		self.plotLayout().setAlignCanvasToScales(True)
		# use custom labelling for frequencies
		self.setAxisScaleDraw(Qwt.QwtPlot.yLeft, FreqScaleDraw())
		self.setAxisScaleDraw(Qwt.QwtPlot.yRight, FreqScaleDraw())
		# set axis titles
		self.setAxisTitle(Qwt.QwtPlot.xBottom, 'Time (s)')
		self.setAxisTitle(Qwt.QwtPlot.yLeft, 'Frequency (Hz)')
		self.enableAxis(Qwt.QwtPlot.yRight)
		# attach a plot image
		self.plotImage = PlotImage()
		self.plotImage.attach(self)
		self.setlinfreqscale()

		self.setAxisScale(Qwt.QwtPlot.xBottom, 0., 10.)
		
		self.picker = Qwt.QwtPlotPicker(Qwt.QwtPlot.xBottom,
                               Qwt.QwtPlot.yLeft,
                               Qwt.QwtPicker.PointSelection,
                               Qwt.QwtPlotPicker.CrossRubberBand,
                               Qwt.QwtPicker.AlwaysOff,
                               self.canvas())
		self.connect(self.picker, QtCore.SIGNAL('moved(const QPoint &)'), self.moved)
		
		self.replot()

	def moved(self, point):
		info = "Time=%d s, Frequency=%d Hz" % (
			self.invTransform(Qwt.QwtPlot.xBottom, point.x()),
			self.invTransform(Qwt.QwtPlot.yLeft, point.y()))
		self.emit(QtCore.SIGNAL("pointerMoved"), info)
		
	def setData(self, xyzs):
		self.plotImage.setData(xyzs)
		self.replot()

	def addData(self, xyzs):
		self.plotImage.addData(xyzs, self.logfreqscale)
		# self.replot() would call updateAxes() which is dead slow (probably because it
		# computes label sizes); instead, let's ask Qt to repaint the canvas only next time
		# This works because we disable the cache
		# TODO what happens when the cache is enabled ?
		# Could that solve the perceived "unsmoothness" ?
		self.canvas().update()

	def setlogfreqscale(self):
		self.plotImage.erase()
		self.logfreqscale = 1
		self.setAxisScaleEngine(Qwt.QwtPlot.yLeft, Qwt.QwtLog10ScaleEngine())
		self.setAxisScale(Qwt.QwtPlot.yLeft, 20., 22050.)
		self.setAxisScaleEngine(Qwt.QwtPlot.yRight, Qwt.QwtLog10ScaleEngine())
		self.setAxisScale(Qwt.QwtPlot.yRight, 20., 22050.)
		self.replot()

	def setlinfreqscale(self):
		#pass
		self.plotImage.erase()
		self.logfreqscale = 0
		self.setAxisScaleEngine(Qwt.QwtPlot.yLeft, Qwt.QwtLinearScaleEngine())
		self.setAxisScale(Qwt.QwtPlot.yLeft, 0., 22050.)
		self.setAxisScaleEngine(Qwt.QwtPlot.yRight, Qwt.QwtLinearScaleEngine())
		self.setAxisScale(Qwt.QwtPlot.yRight, 0., 22050.)
		self.replot()
