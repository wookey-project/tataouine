# Import our local utils
import sys, os, inspect
FILENAME = inspect.getframeinfo(inspect.currentframe()).filename
SCRIPT_PATH = os.path.dirname(os.path.abspath(FILENAME)) + "/"

from fido_sd_manager import *

#################################
# GUI
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import * 
from PIL.ImageQt import ImageQt
from math import ceil

from PyQt5.QtCore import QThread

# For parsing JSON
import glob
import json

# Thread worker to get all the slots (possibly long running, hence the thread)
class Worker(QObject):
    finished = pyqtSignal()
    def __init__(self, mainwindow, progressbar):
        super().__init__()
        self.mainwindow = mainwindow
        self.progressbar = progressbar
        self.do_exit = False
    def curr_slot_progress(self, n, m):
        self.progressbar.setWindowTitle("Please wait, loading active slots %d / %d (maximum %d)" % (n, self.max_active_slots, m))
        self.progressbar.progress.setValue(int((n / self.max_active_slots) * 100.00))
        if self.do_exit == True:            
            return True
        return False
    def run(self):
        self.max_active_slots = get_num_active_slots(self.mainwindow.key, self.mainwindow.device)
        self.mainwindow.curr_slots = dump_slots(self.mainwindow.key, self.mainwindow.device, check_hmac=True, verbose=False, curr_slot_progress = self.curr_slot_progress)
        self.finished.emit()


#############
class ProgressBar(QWidget):
    def close_pbar(self):
        self.mainwindow.subaction = False
        self.worker.do_exit = True
        self.thread.terminate()
    def closeEvent(self, evnt):
        self.close_pbar()
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.mainwindow.subaction = True

        # We have to set the size of the main window
        # ourselves, since we control the entire layout
        self.setMinimumSize(400, 185)
        self.setWindowTitle("Please wait, loading slots ...")

        # Make window on top
        self.setWindowModality(Qt.ApplicationModal)

        self.progress = QProgressBar(self)
        self.progress.setGeometry(200, 80, 250, 20)
        
        self.thread = QThread()
        self.worker = Worker(self.mainwindow, self)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.thread_finished)

        self.thread.start()
        
        self.cancel = QPushButton('Cancel', self)
        self.cancel.clicked.connect(self.cancel_clicked)
        self.cancel.setMinimumWidth(145)
        self.cancel.move(250, 150)

    def thread_finished(self):
        self.mainwindow.refresh(post_progress = True)
        self.close()
    def cancel_clicked(self):
        self.close_pbar()
        self.close()

#############
class LoadData(QWidget):
    def closeEvent(self, evnt):
        self.mainwindow.subaction = False
        self.close()
    def __init__(self, slot_idx, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.mainwindow.subaction = True

        # We have to set the size of the main window
        # ourselves, since we control the entire layout
        self.setMinimumSize(400, 185)
        self.setWindowTitle("Load data from SD")
        
        # Make window on top
        self.setWindowModality(Qt.ApplicationModal)

        X_shift_lbl = 5
        X_shift = 180
        Y_shift = 30
        min_w = 500 
        Y_shift_delta = 50

        # Choose SD path
        self.sd_path_lbl = QLabel("SD path:", self)
        self.sd_path_lbl.move(X_shift_lbl, Y_shift)
        self.sd_path = QLineEdit(self)
        self.sd_path.setMinimumWidth(min_w)
        self.sd_path.move(X_shift, Y_shift)
        self.sd_path.setText("/tmp/sd.dump")
        Y_shift += Y_shift_delta

        # Pet PIN
        self.petpin_lbl = QLabel("Pet PIN:", self)
        self.petpin_lbl.move(X_shift_lbl, Y_shift)
        self.petpin = QLineEdit(self)
        self.petpin.setMinimumWidth(min_w)
        self.petpin.move(X_shift, Y_shift)
        self.petpin.setText("1234")
        Y_shift += Y_shift_delta

        # User PIN
        self.userpin_lbl = QLabel("User PIN:", self)
        self.userpin_lbl.move(X_shift_lbl, Y_shift)
        self.userpin = QLineEdit(self)
        self.userpin.setMinimumWidth(min_w)
        self.userpin.move(X_shift, Y_shift)
        self.userpin.setText("1234")
        Y_shift += Y_shift_delta

        # Keys path
        self.keys_path_lbl = QLabel("Token keys path:", self)
        self.keys_path_lbl.move(X_shift_lbl, Y_shift)
        self.keys_path = QLineEdit(self)
        self.keys_path.setMinimumWidth(min_w)
        self.keys_path.move(X_shift, Y_shift)
        self.keys_path.setText(SCRIPT_PATH+"../private")
        Y_shift += Y_shift_delta

        # Provide master key choice
        self.mkey_checkbox = QCheckBox("", self)
        self.mkey_checkbox.move(X_shift_lbl+40, Y_shift+5)
        self.mkey_checkbox.setChecked(False)
        self.mkey_checkbox.stateChanged.connect(self.mkey_checkbox_changed)
        self.mkey_checkbox.setText("Check to provide your known master key (no token)")
        self.mkey_checkbox.setToolTip("Check to provide your master key without token")
        Y_shift += Y_shift_delta

        # Provide master key
        self.mkey_lbl = QLabel("Master key:", self)
        self.mkey_lbl.move(X_shift_lbl, Y_shift)
        self.mkey = QLineEdit(self)
        self.mkey.setMinimumWidth(min_w)
        self.mkey.move(X_shift, Y_shift)
        self.mkey_lbl.setDisabled(True)
        self.mkey.setDisabled(True)
        self.mkey.setText("aa"*32)
        Y_shift += Y_shift_delta


        # Button
        self.apply_mod = QPushButton('OK', self)
        self.apply_mod.clicked.connect(self.ok_clicked)
        self.apply_mod.setMinimumWidth(145)
        self.apply_mod.move(250, Y_shift)

        self.cancel = QPushButton('Cancel', self)
        self.cancel.clicked.connect(self.cancel_clicked)
        self.cancel.setMinimumWidth(145)
        self.cancel.move(450, Y_shift)

    def user_feed_back_token(self, pet_name):
        # 
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("The PET name in your token is\n'%s'\ncorrect?" % pet_name)
        msg.setInformativeText("Beware that a bad PET name could mean phishing!! Do not accept if not sure ...")
        msg.setWindowTitle("PET Name validation")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()
        if retval == 0x400:
            return True
        else:
            return False
    def ok_clicked(self, event):
        # Check if SD path is good
        if os.path.isfile(self.sd_path.text()) == False:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("SD file error")
            msg.setInformativeText("SD file path %s does not exist!" % self.sd_path.text())
            msg.setText("Please provide a proper path to your SD device file")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retval = msg.exec_()
            return
        # Do we use token or not?
        key = None
        if self.mkey_checkbox.isChecked() == True:
            # Check if provided master key is OK
            try:
                key = binascii.unhexlify(self.mkey.text().encode('latin-1'))
                if len(key) != 32:
                    raise Exception('Master key error')
                key = key.decode('latin-1')
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Master key error")
                msg.setInformativeText("Master seems to have bad format ...")
                msg.setText("Please provide a 32 bytes key (in hexadecimal form)")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                retval = msg.exec_()
                return
        else:
            # Check if token is here
            card = try_connect_to_token(verbose=False)
            if card == None:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Token is not not detected!")
                msg.setInformativeText("The token is necessary to get the cryptographic keys for reading the SD")
                msg.setText("Please insert a proper AUTH token")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                retval = msg.exec_()
                return
            # If yes, go on
            try:
                key, _, _ = FIDO_token_get_assets("auth", self.keys_path.text(), self.petpin.text(), self.userpin.text(), user_feed_back = self.user_feed_back_token)
                key = key[:32]
            except:
                pass
            if key == None:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Token error")
                msg.setInformativeText("Something bad happened when communicating with the token ...")
                msg.setText("Please insert a proper AUTH token")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                retval = msg.exec_()
                return      
        self.mainwindow.device = self.sd_path.text()
        self.mainwindow.key = key
        QTimer.singleShot(300, self.mainwindow.refresh)
        self.close()

    def cancel_clicked(self, event):
        self.close()

    def mkey_checkbox_changed(self, event):
        if self.mkey_checkbox.isChecked() == True:
            self.petpin_lbl.setDisabled(True)         
            self.petpin.setDisabled(True)
            self.userpin_lbl.setDisabled(True)         
            self.userpin.setDisabled(True)         
            self.keys_path_lbl.setDisabled(True)         
            self.keys_path.setDisabled(True)
            self.mkey_lbl.setDisabled(False)
            self.mkey.setDisabled(False)
        else:
            self.petpin_lbl.setDisabled(False)         
            self.petpin.setDisabled(False)
            self.userpin_lbl.setDisabled(False)         
            self.userpin.setDisabled(False)         
            self.keys_path_lbl.setDisabled(False)         
            self.keys_path.setDisabled(False)
            self.mkey_lbl.setDisabled(True)
            self.mkey.setDisabled(True)
        return

#############
U2F_APPID_DB_PATH = SCRIPT_PATH + "fido_db/"
class SelectExisting(QWidget):
    def closeEvent(self, evnt):
        self.close()
    def __init__(self, upwindow):
        super().__init__()
        self.upwindow = upwindow
        self.setMinimumSize(400, 185)

        # icon
        self.icon = QLabel(self)
        #self.icon.setStyleSheet("border: 1px solid black;")
        self.icon.setFixedSize(45, 45)
        self.icon.move(150, 15)

        # Make window on top
        self.setWindowModality(Qt.ApplicationModal)
        layout = QHBoxLayout()
        self.cb = QComboBox()
        self.cb.currentIndexChanged.connect(self.selectionchange)
        # Get all our existing relying parties
        sys.path.append(U2F_APPID_DB_PATH)
        import fido_db
        for a in fido_db.u2f_rp_database:
            self.cb.addItem(a['name'])
        layout.addWidget(self.cb)
        self.setLayout(layout)
        self.setWindowTitle("Select a known Relying Party")
         
        Y_shift = 130
        self.ok = QPushButton('OK', self)
        self.ok.clicked.connect(self.ok_clicked)
        self.ok.setMinimumWidth(145)
        self.ok.move(50, Y_shift)
   
        self.cancel = QPushButton('Cancel', self)
        self.cancel.clicked.connect(self.cancel_clicked)
        self.cancel.setMinimumWidth(145)
        self.cancel.move(200, Y_shift)


    def selectionchange(self, i):
        sys.path.append(U2F_APPID_DB_PATH)
        import fido_db        
        self.current_selection = fido_db.u2f_rp_database[i]
        if (len(fido_db.u2f_rp_database[i]['logo']) != 0):
            # Normalize the logo
            buff = binascii.unhexlify(fido_db.u2f_rp_database[i]['logo'])
            icon, _, _ = RLE_compress_buffer(buff, target_dim=(45, 45))
            img, img_class = RLE_uncompress_buffer(icon, target_dim=(45,45))
            img = img.convert("RGBA")
            qimg = ImageQt(img)
            pix = QPixmap.fromImage(qimg)
            self.icon.setPixmap(pix)
            self.logo_set = pix
        else:
            pix = QPixmap(45, 45)
            pix.fill(QColor(0,0,0,0))
            self.icon.setPixmap(pix)
            self.logo_set = None

    def cancel_clicked(self):
        self.close()
        return
    def ok_clicked(self):
        self.upwindow.appid.setText(self.current_selection['appid'])
        self.upwindow.name.setText(self.current_selection['name'])
        self.upwindow.url.setText(self.current_selection['url'])
        if self.logo_set != None:
            self.upwindow.icon_checkbox.setChecked(True)
            self.upwindow.icon.setPixmap(self.logo_set)
            self.upwindow.icon_type = "RLE"
        else:
            self.upwindow.icon_checkbox.setChecked(False)
            self.upwindow.icon_type = "NONE"

        self.close()
        return

#############
class EditSlot(QWidget):
    def closeEvent(self, evnt):
        self.mainwindow.subaction = False
        self.close()
    def __init__(self, slot_idx, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.mainwindow.subaction = True
        if slot_idx == None: 
            # This is a new slot
            self.slot = None
        else:
            self.mainwindow = mainwindow
            self.slot = mainwindow.curr_slots[slot_idx]
            i, appid, slotid, slotaddr, appid_slot = self.slot

        # We have to set the size of the main window
        # ourselves, since we control the entire layout
        self.setMinimumSize(400, 185)
        if slot_idx != None: 
            self.setWindowTitle("Edit Slot %d" % i)
        else:
            self.setWindowTitle("Add new slot")

        # Make window on top
        self.setWindowModality(Qt.ApplicationModal)

        X_shift_lbl = 5
        X_shift = 110
        Y_shift = 30
        min_w = 500 
        Y_shift_delta = 50

        self.appid_lbl = QLabel("appid:", self)
        self.appid_lbl.move(X_shift_lbl, Y_shift)
        self.appid = QLineEdit(self)
        if slot_idx != None: 
            self.appid.setText("%s" % binascii.hexlify(appid_slot.serialize('appid')).decode("latin-1"))
        self.appid.setMinimumWidth(min_w)
        self.appid.move(X_shift, Y_shift)
        Y_shift += Y_shift_delta

        self.kh_lbl = QLabel("kh:", self)
        self.kh_lbl.move(X_shift_lbl, Y_shift)
        self.kh = QLineEdit(self)
        if slot_idx != None: 
            self.kh.setText("%s" % binascii.hexlify(appid_slot.serialize('kh')).decode("latin-1"))
        self.kh.setMinimumWidth(min_w)
        self.kh.move(X_shift, Y_shift)
        Y_shift += Y_shift_delta

        self.name_lbl = QLabel("name:", self)
        self.name_lbl.move(X_shift_lbl, Y_shift)
        self.name = QLineEdit(self)
        if slot_idx != None: 
            self.name.setText("%s" % appid_slot.serialize('name').decode("latin-1").rstrip('\x00'))
        self.name.setMinimumWidth(min_w)
        self.name.move(X_shift, Y_shift)
        Y_shift += Y_shift_delta

        self.url_lbl = QLabel("url:", self)
        self.url_lbl.move(X_shift_lbl, Y_shift)
        self.url = QLineEdit(self)
        if slot_idx != None: 
            self.url.setText("%s" % appid_slot.serialize('url').decode("latin-1").rstrip('\x00'))
        self.url.setMinimumWidth(min_w)
        self.url.move(X_shift, Y_shift)
        Y_shift += Y_shift_delta

        self.ctr_lbl = QLabel("ctr:", self)
        self.ctr_lbl.move(X_shift_lbl, Y_shift)
        self.ctr = QLineEdit(self)
        if slot_idx != None: 
            self.ctr.setText("%d" % appid_slot.ctr)
        else:
            self.ctr.setText("0")
        self.ctr.setMinimumWidth(min_w)
        self.ctr.move(X_shift, Y_shift)
        Y_shift += Y_shift_delta
 
        self.flags_lbl = QLabel("flags:", self)
        self.flags_lbl.move(X_shift_lbl, Y_shift)
        self.flags = QLineEdit(self)
        if slot_idx != None: 
            self.flags.setText("%d" % appid_slot.flags)
        else:
            self.flags.setText("0")
        self.flags.setMinimumWidth(min_w)
        self.flags.move(X_shift, Y_shift)
        Y_shift += Y_shift_delta
       
         
        self.icon_lbl = QLabel("icon:", self)
        self.icon_lbl.move(X_shift_lbl, Y_shift)

        self.icon_checkbox = QCheckBox("", self)
        self.icon_checkbox.move(X_shift_lbl+40, Y_shift+5)
        self.icon_checkbox.setChecked(False)
        self.icon_checkbox.stateChanged.connect(self.icon_checkbox_changed)
        self.icon_checkbox.setToolTip("Check to embed icon (image or RGB)")

        self.icon = QLabel(self)
        self.icon.setStyleSheet("border: 1px solid black;")
        self.icon.setCursor(QCursor(Qt.PointingHandCursor))
        self.icon.setToolTip("Left click for icon file select.\nRight click for RGB color select.")
        self.icon.mouseReleaseEvent = self.change_icon_clicked
        self.icon.setFixedSize(45, 45)
        self.icon_type = "NONE"
        self.icon_rgb = None
        
        if (slot_idx != None):
            if inverse_mapping(icon_types)[appid_slot.icon_type] == 'RGB':
                self.icon_checkbox.setChecked(True)
                self.icon_type = "RGB"
                rgb = appid_slot.serialize('icon')
                (r, g, b) = (rgb[0], rgb[1], rgb[2])
                self.icon_rgb = (r, g, b)
                background = Image.new("RGBA", (45, 45), (r, g, b))
                qimg = ImageQt(background)
                pix = QPixmap.fromImage(qimg)
                self.icon.setPixmap(pix)              
            elif inverse_mapping(icon_types)[appid_slot.icon_type] == 'RLE':
                self.icon_checkbox.setChecked(True)
                self.icon_type = "RLE"
                # Uncompress our RLE data
                img, img_class = RLE_uncompress_buffer(appid_slot.serialize('icon')[:appid_slot.icon_len], target_dim=(45,45))
                img = img.convert("RGBA")
                qimg = ImageQt(img)
                pix = QPixmap.fromImage(qimg)
                self.icon.setPixmap(pix)
            else:
                self.icon_checkbox.setChecked(False)
                self.icon_type = "NONE"

        self.icon.move(X_shift, Y_shift)
        Y_shift += Y_shift_delta      

        if self.icon_checkbox.isChecked() == False:
            # Select icon disabled by default
            self.icon_lbl.setDisabled(True)  
            self.icon.setDisabled(True)


        if slot_idx != None:
            self.apply_mod = QPushButton('Apply modifications', self)
        else:
            self.apply_mod = QPushButton('Add the new slot   ', self)
        self.apply_mod.clicked.connect(self.apply_clicked)
        self.apply_mod.setMinimumWidth(145)
        self.apply_mod.move(250, Y_shift)

        if slot_idx != None:
            self.delete = QPushButton('Delete slot', self)
            self.delete.clicked.connect(self.delete_clicked)
            self.delete.setMinimumWidth(145)
            self.delete.move(450, Y_shift)
        else:
            self.load_existing = QPushButton('Load existing', self)
            self.load_existing.clicked.connect(self.load_existing_clicked)
            self.load_existing.setMinimumWidth(145)
            self.load_existing.move(450, Y_shift)

        self.cancel = QPushButton('Cancel', self)
        self.cancel.clicked.connect(self.cancel_clicked)
        self.cancel.setMinimumWidth(145)
        self.cancel.move(605, Y_shift)

    def icon_checkbox_changed(self, event):
        if self.icon_checkbox.isChecked() == False:
            self.icon_lbl.setDisabled(True)         
            self.icon.setDisabled(True)         
        else:
            self.icon_lbl.setDisabled(False)
            self.icon.setDisabled(False)
        return

    def load_existing_clicked(self, event):
        print("Load existing clicked")
        # Show the user the known appids parsed from the dedicated folder
        self.select = SelectExisting(self)
        self.select.show()
        return

    def cancel_clicked(self, event):
        self.close()

    def change_icon_clicked(self, event):
        print("Change icon clicked")
        if event.button() == Qt.LeftButton:
            filedialog = QFileDialog(self)
            #filedialog.setDefaultSuffix("png")
            filedialog.setNameFilter("Icon files (*.png *.jpg *.jpeg);;All files (*.*)")
            selected = filedialog.exec()
            if selected:
                filename = filedialog.selectedFiles()[0]
            else:
                return
            # Convert to RLE and back an show
            self.icon_type = "RLE"
            with open(filename, "rb") as f:
                icon, _, _ = RLE_compress_buffer(f.read(), target_dim=(45, 45))
                img, img_class = RLE_uncompress_buffer(icon, target_dim=(45,45))            
            img = img.convert("RGBA")
            qimg = ImageQt(img)
            pix = QPixmap.fromImage(qimg)
            self.icon.setPixmap(pix)
        else:
            # Color picker for "RGB"
            color = QColorDialog.getColor()
            if color.isValid() == True:
                self.icon_type = "RGB"
                (r, g, b) = (color.red(), color.green(), color.blue())
                self.icon_rgb = (r, g, b)
                background = Image.new("RGBA", (45, 45), (r, g, b))
                qimg = ImageQt(background)
                pix = QPixmap.fromImage(qimg)
                self.icon.setPixmap(pix)
       
    def delete_clicked(self):
        print("Delete clicked")
        i, appid, slotid, slotaddr, appid_slot = self.slot
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Are you sure you want to delete slot %d?" % i)
        msg.setInformativeText("This action is irreversible!")
        msg.setWindowTitle("Slot %d delete" % i)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()
        if retval == 0x400:
            check = remove_appid(self.mainwindow.key, self.mainwindow.device, appid=appid, slot_num=i, check_hmac=True)
            # Refresh main window and quit
            self.mainwindow.refresh(index=[i]) 
            self.close()
     

    def apply_clicked(self):
        print("Apply clicked")
        if self.slot != None:
            # Edit existing slot
            i, appid, slotid, slotaddr, appid_slot = self.slot
            slot_num = i
        else:
            # New slot
            slot_num = None
        if (self.icon_checkbox.isChecked() == True) and (self.icon_type == "RGB"):
            r, g, b = self.icon_rgb
            icon = bytearray([r, g, b]) 
        elif (self.icon_checkbox.isChecked() == True) and (self.icon_type == "RLE"):
            ba = QByteArray()
            buff = QBuffer(ba)
            buff.open(QIODevice.WriteOnly) 
            self.icon.pixmap().save(buff, "PNG")
            self.icon.show()
            icon, _, _ = RLE_compress_buffer(ba.data(), target_dim=(45, 45))
        else:
            icon = None
        kh = None
        if len(self.kh.text()) == 0:
            kh_ = b"\x00"*32
        else:
            kh_ = binascii.unhexlify(self.kh.text())
            kh = binascii.unhexlify(self.kh.text())
        # Check if we have been asked to add an existing appid with kh
        _, _, check_slot = get_SD_appid_slot(self.mainwindow.key, self.mainwindow.device, appid=binascii.unhexlify(self.appid.text()), kh=kh_, check_hmac=False)
        if (check_slot != None) and (check_slot != slot_num):
            # Tell the user this is not possible
            warning_dialog = QMessageBox()
            warning_dialog.setIcon(QMessageBox.Critical)
            if slot_num != None:
                warning_dialog.setText("Modifying slot %d" % slot_num)
            else:
                warning_dialog.setText("Adding slot")
            warning_dialog.setInformativeText("Appid:\n%s with\nKH:\n%s\nalready exists in slot %d\nAdding a duplicate is forbidden" % (self.appid.text(), self.kh.text(), check_slot)) 
            warning_dialog.setWindowTitle("Error")
            warning_dialog.exec_()
            return
        error = False
        try:
            check, num, _, _ = update_appid(self.mainwindow.key, self.mainwindow.device, binascii.unhexlify(self.appid.text()), slot_num=slot_num, ctr=int(self.ctr.text()), flags=int(self.flags.text()), icon=icon, name=self.name.text().encode('latin-1'), url=self.url.text().encode('latin-1'), kh = kh, check_hmac=True)
        except:
            error = True
        if (error == True) or (num == None):
            # Report an error
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            if slot_num != None:
                error_dialog.setText("Error modifying slot %d" % slot_num)
            else:
                error_dialog.setText("Error adding slot")
            error_dialog.setInformativeText("An error occured: have you correctly filled all the slot inputs?\n-kh is optional, must be 64 hexadecimal long)")
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()
            return
           
        # Refresh main window and quit
        self.mainwindow.refresh(index=[num]) 
        self.close()


class ItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.decorationPosition = QStyleOptionViewItem.Right
        super(ItemDelegate, self).paint(painter, option, index)

class Window(QWidget):
    def closeEvent(self, evnt):
        self.close()
        sys.exit(0)
    def __init__(self):
        super(QWidget, self).__init__()
        self.w = None # No external window yet
        layout = QGridLayout()
        self.setLayout(layout)       
        self.listwidget = QListWidget()
        self.key = None
        self.device = None
        self.refresh()
        self.delegate = ItemDelegate()
        self.listwidget.setItemDelegate(self.delegate)
        self.listwidget.itemDoubleClicked.connect(self.double_clicked)
        self.listwidget.mouseReleaseEvent = self.mousePressEvent
        layout.addWidget(self.listwidget)
        self.right_click = False
        self.left_click = False
        self.subaction = False

    def mousePressEvent(self, event):
        if self.key == None or self.device == None:
            self.w = LoadData(None, self)
            self.w.show()
        if event.button() == Qt.LeftButton:
            self.left_click = True
            self.right_click = False
        elif event.button() == Qt.RightButton:
            self.right_click = True
            self.left_click = False
            if self.subaction == False:
                self.w = EditSlot(None, self)
                self.w.show()               

    def double_clicked(self, qmodelindex):
        if self.left_click == True: 
            item = self.listwidget.currentItem()
            if self.subaction == False:
                self.w = EditSlot(self.listwidget.currentRow(), self)
                self.w.show()

    def refresh(self, index=None, post_progress=False):
        if self.key == None or self.device == None:
            return
        if index == None and post_progress == False:
            self.curr_slots = None
            # Refresh everything
            self.listwidget.clear()
            #
            self.w = ProgressBar(self)
            self.w.show()
            return
        elif index != None:
            # Only refresh modified slots
            self.listwidget.clear()
            modified_slots = dump_slots(self.key, self.device, slot_num=index, check_hmac=True, verbose=True)
            if modified_slots == None:
                modified_slots = []
            curr_slots_copy = self.curr_slots
            self.curr_slots = []
            old_index = []
            for s in curr_slots_copy:
                i, appid, slotid, slotaddr, appid_slot = s
                old_index.append(i)
            for s in curr_slots_copy:
                i, appid, slotid, slotaddr, appid_slot = s
                if i in index:
                    for ms in modified_slots:
                        j, _, _, _, _ = ms
                        if i == j:
                            self.curr_slots.append(ms)
                else:
                    self.curr_slots.append(s)
            # Add new slots
            for ms in modified_slots:
                j, _, _, _, _ = ms
                if not (j in old_index):
                    self.curr_slots.append(ms)
        if self.curr_slots == None:
            # There was an error when decoding ...
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("SD decoding error")
            msg.setInformativeText("An unknown error occured when decoding SD slots!")
            msg.setText("1) Please check that your token or the provided key match, and try again.\n2) If you canceled SD decoding, please try again and let it finish.")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retval = msg.exec_()
            self.key = self.device = None
            return

        # Sort current slots by slot number increasing order
        self.curr_slots = sorted(self.curr_slots, key=lambda tup: tup[0])
        idx = 0
        for s in self.curr_slots:
            i, appid, slotid, slotaddr, appid_slot = s
            if inverse_mapping(icon_types)[appid_slot.icon_type] == 'RGB':
                rgb = appid_slot.serialize('icon')
                (r, g, b) = (rgb[0], rgb[1], rgb[2])
                background = Image.new("RGBA", (45, 45), (r, g, b))
                qimg = ImageQt(background)
                pix = QPixmap.fromImage(qimg)
                icon = QIcon()
                icon.addPixmap(pix)              
            elif inverse_mapping(icon_types)[appid_slot.icon_type] == 'RLE':
                # Uncompress our RLE data
                img, img_class = RLE_uncompress_buffer(appid_slot.serialize('icon')[:appid_slot.icon_len], target_dim=(45,45))
                img = img.convert("RGBA")
                qimg = ImageQt(img)
                pix = QPixmap.fromImage(qimg)
                #pix.scaledToHeight(120, mode=Qt.SmoothTransformation) 
                icon = QIcon()
                icon.addPixmap(pix)
            elif inverse_mapping(icon_types)[appid_slot.icon_type] == 'NONE':
                icon = QIcon()
            
            item = QListWidgetItem(icon, "Slot %04d, Slotid='@0x%08x', Appid='%s', name='%s'" % (i, slotid, binascii.hexlify(appid).decode("latin-1"), appid_slot.serialize('name').decode("latin-1").rstrip('\x00')))
            self.listwidget.insertItem(idx, item)            
            idx += 1

        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font  = QFont("monospace")
    app.setFont(font)
    window = Window()
    #window.resize(900, 900)
    window.showMaximized()
    window.setWindowTitle('U2F2 FIDO configurator')
    
    window.show()
    sys.exit(app.exec_())
