from utils.vec import vec
from PyQt6.QtWidgets import QMainWindow

class Window:
    def get_window_size(self):
        size = self.ui_window.size()
        return vec(size.width(), size.height())
    
    def get_window_offset(self):
        offset = self.ui_window.geometry()
        return vec(offset.x(), offset.y())
    
    def SetupWindow(self):
        window_config = self.ui_window.config.data['window']
        do_reset = False

        if 'size' in window_config:
            if 'width' in window_config['size']: window_width = int(window_config['size']['width'])
            else: do_reset = True
            
            if 'width' in window_config['size']: window_height = int(window_config['size']['height'])
            else: do_reset = True

            if 'offset' in window_config:
                if 'left' in window_config['offset']: window_offset_left = int(window_config['offset']['left'])
                else: do_reset = True

                if 'top' in window_config['offset']: window_offset_top = int(window_config['offset']['top'])
                else: do_reset = True

            if not do_reset:
                self.ui_window.setWindowTitle('KAG Map Maker')
                self.ui_window.setGeometry(window_offset_left, window_offset_top, window_width, window_height) # offsets x,y & width,height
        else:
            do_reset = True

        if do_reset:
            self.ui_window.config.reset()