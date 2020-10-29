from kivy.core.window import Window
from kivy.config import Config
from random import *
from functools import partial
from kivy.graphics import Rectangle, Color, Canvas
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.app import App
import kivy
import re
# kivy.require('1.7.2')


#setup graphics
Config.set('graphics', 'resizable', 0)

#Graphics fix
Window.clearcolor = (0, 0, 0, 1.)
#Window.clearcolor = (1,0,0,1.)


class MyButton(Button):
   #class used to get uniform button styles
   def __init__(self, **kwargs):
      super(MyButton, self).__init__(**kwargs)
      self.font_size = Window.width*0.018


class MyText(TextInput):
   #class used to get uniform button styles
   def __init__(self, **kwargs):
      super(MyText, self).__init__(**kwargs)
      self.font_size = Window.width*0.018

   pat = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

   def insert_text(self, substring, from_undo=False):
       pat = self.pat
       if '.' in self.text:
           s = re.sub(pat, '', substring)
       else:
           s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
       return super(MyText, self).insert_text(s, from_undo=from_undo)


class SmartMenu(Widget):
   #the instance created by this class will appear
   #when the game is started for the first time
   buttonList = []

   def __init__(self, **kwargs):
      #create custom events first
      # creating a custom event called 'on_button_release' that will be used to pass information from the menu to the parent instance
      super(SmartMenu, self).__init__(**kwargs)
      self.layout = BoxLayout(orientation='vertical')
      self.layout.background_color = [1, 1, 1, 1]
      self.layout.width = Window.width/2
      self.layout.height = Window.height/2
      self.layout.x = Window.width/2 - self.layout.width/2
      self.layout.y = Window.height/2 - self.layout.height/2
      self.add_widget(self.layout)
      self.register_event_type('on_button_release')

   def on_button_release(self, *args):
      #print 'The on_button_release event was just dispatched', args
      #don't need to do anything here. needed for dispatch
      pass

   def callback(self, instance):
      #print('The button %s is being pressed' % instance.text)
      self.buttonText = instance.text
      # dispatching the callback event 'on_button_release' to tell teh parent instance to read the button text
      self.dispatch('on_button_release')

   def addButtons(self):
      self.txt = MyText(text='192.168.0.100', multiline=False)
      self.layout.add_widget(self.txt)
      for k in self.buttonList:
         tmpBtn = MyButton(text=k)
         tmpBtn.background_color = [.4, .4, .4, .4]
         # when the button is released the callback function is called
         tmpBtn.bind(on_release=self.callback)
         self.layout.add_widget(tmpBtn)

   def buildUp(self):
      #self.colorWindow()
      self.addButtons()


class SmartStartMenu(SmartMenu):
   #setup the menu button names
   buttonList = ['Join', 'Start']

   def __init__(self, **kwargs):
      super(SmartStartMenu, self).__init__(**kwargs)
      self.layout = BoxLayout(orientation='vertical')
      self.layout.background_color = [1, 1, 1, 1]
      self.layout.width = Window.width/5
      self.layout.height = Window.height/5
      self.layout.x = Window.width/2 - self.layout.width/2
      self.layout.y = Window.height/2 - self.layout.height/2
      self.add_widget(self.layout)

      self.msg = Label(text='Sequence')
      self.msg.font_size = Window.width*0.07
      self.msg.pos = (Window.width*0.45, Window.height*0.75)
      self.add_widget(self.msg)
