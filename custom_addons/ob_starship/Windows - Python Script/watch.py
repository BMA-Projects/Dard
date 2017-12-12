"""Working example of the ReadDirectoryChanges API which will
 track changes made to a directory. Can either be run from a
 command-line, with a comma-separated list of paths to watch,
 or used as a module, either via the watch_path generator or
 via the Watcher threads, one thread per path.

Examples:
  watch_directory.py c:/temp,r:/images

or:
  import watch_directory
  for file_type, filename, action in watch_directory.watch_path ("c:/temp"):
    print filename, action

or:
  import watch_directory
  import Queue
  file_changes = Queue.Queue ()
  for pathname in ["c:/temp", "r:/goldent/temp"]:
    watch_directory.Watcher (pathname, file_changes)

  while 1:
    file_type, filename, action = file_changes.get ()
    print file_type, filename, action

(c) Tim Golden - mail at timgolden.me.uk 5th June 2009
Licensed under the (GPL-compatible) MIT License:
http://www.opensource.org/licenses/mit-license.php
"""
from __future__ import generators
import os
import sys
import Queue
import threading
import time
import xmltodict
import json
import win32file
import win32con

import xmlrpclib
import base64
import sys
import codecs
import os, shutil
import os.path

folder = 'D:/Starship_Shipping_Files'


sys.stdout = codecs.getwriter('utf8')(sys.stdout)

ACTIONS = {
  1 : "Created",
  2 : "Deleted",
  3 : "Updated",
  4 : "Renamed to something",
  5 : "Renamed from something"
}

url = 'http://172.16.120.64:8069'
dbname = 'dard_test10112016'
username = 'admin'
pwd = 'a'

sock_common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
sock = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
uid = sock_common.login(dbname, username, pwd)

def watch_path (path_to_watch, include_subdirectories=False):
  FILE_LIST_DIRECTORY = 0x0001
  hDir = win32file.CreateFile (
    path_to_watch,
    FILE_LIST_DIRECTORY,
    win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
    None,
    win32con.OPEN_EXISTING,
    win32con.FILE_FLAG_BACKUP_SEMANTICS,
    None
  )
  while 1:
    print "-=============Shipping Script Started=========="
    results = win32file.ReadDirectoryChangesW (
      hDir,
      1024,
      include_subdirectories,
      win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
      None,
      None
    )
    for action, file in results:
      print "file---", file
      if action == 1 or action == 3 and file.startswith('ShipResult'):
        full_filename = os.path.join (path_to_watch, file)
        if not os.path.exists (full_filename):
          file_type = "<deleted>"
        elif os.path.isdir (full_filename):
          file_type = 'folder'
        else:
          file_type = 'file'
        yield (file_type, full_filename, ACTIONS.get (action, "Unknown"))
        #print "Path", os.path.isfile('D:/Starship_Shipping_Files/ShipResult.XML')
        if os.path.isfile('D:/Starship_Shipping_Files/ShipResultT.XML'):
          f_name_r = 'D:/Starship_Shipping_Files/ShipResultT.XML'
        else:
          f_name_r = 'D:/Starship_Shipping_Files/ShipResult.XML'
        with open(f_name_r, "r") as myfile:
          data= myfile.read()
          myfile.close()
        file_data = base64.b64encode(data)
        read_file = open(f_name_r, "r+")
        file_content = read_file.read()
        xml_parse = xmltodict.parse(file_content)
        result = json.dumps(xml_parse)
        result = json.loads(result)
        read_file.close()
        tracking_id = False
        o_id = False
        for name_value in result.get('WriteShipment', '').get('SourceDocument', '').get('FreightInfo', '').get('Shipment', '').get('NameValue', ''):
          if name_value.get('@Name', '') == 'Order Number':
            o_id = name_value.get('@Value','Empty')
            print "ORDER ::", o_id
          if name_value.get('@Name', '') == 'TrackingNumber':
            tracking_id = name_value.get('@Value','Empty')
            print "Tracking ID ::", tracking_id
        if tracking_id:
          print "-----Update BMA with Starship-----"
          id = sock.execute_kw(dbname, uid, pwd, 'ir.attachment', 'create', [{'name': file,'datas_fname': file,'res_model': 'sale.order','res_id': int(o_id), 'datas': file_data}])
          sock.execute_kw(dbname, uid, pwd, 'sale.order', 'write', [[int(o_id)], {'is_shipped': True}])

class Watcher (threading.Thread):

  def __init__ (self, path_to_watch, results_queue, **kwds):
    threading.Thread.__init__ (self, **kwds)
    self.setDaemon (1)
    self.path_to_watch = path_to_watch
    self.results_queue = results_queue
    self.start ()

  def run (self):
    for result in watch_path (self.path_to_watch):
      self.results_queue.put (result)

if __name__ == '__main__':
  """If run from the command line, use the thread-based
   routine to watch the current directory (default) or
   a list of directories specified on the command-line
   separated by commas, eg

   watch_directory.py c:/temp,c:/
  """
  PATH_TO_WATCH = ["D:/Starship_Shipping_Files"]
  try: path_to_watch = sys.argv[1].split (",") or PATH_TO_WATCH
  except: path_to_watch = PATH_TO_WATCH
  path_to_watch = [os.path.abspath (p) for p in path_to_watch]
  print "Watching %s at %s" % (", ".join (path_to_watch), time.asctime ())
  files_changed = Queue.Queue ()

  for p in path_to_watch:
    Watcher (p, files_changed)

  while 1:
    try:
      file_type, filename, action = files_changed.get_nowait ()
      print file_type, filename, action
    except Queue.Empty:
      pass
    time.sleep (1)


