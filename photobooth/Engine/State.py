

class State:
    def __init__(self,seq,seq_popup,ftl):
        self.timeline = 0
        self.popupline = ''
        self.seq = seq
        self.ftl = ftl 
        self.seq_popup = seq_popup
        self.state = self.seq[self.timeline]
        self.last_state = ''
        self.list_popup = []

    def next(self):
        self.timeline = self.timeline + 1
        self.state = self.seq[self.timeline]
        self.show()

    def back(self):
        self.timeline = self.timeline - 1
        self.state = self.seq[self.timeline]
        self.show()
   
    def restart(self):
        self.timeline = 0
        self.state = self.seq[self.timeline]
        self.list_popup = []
        self.show()

    def show(self):
        if self.last_state != self.state:
            self.last_state = self.state
            self.ftl(self.state)


    def popup(self,seq_popup_name):
        if seq_popup_name not in self.list_popup:
            self.list_popup.append(seq_popup_name)
            print("ajout de popup : {}",self.list_popup)
        self.state = self.seq_popup[self.list_popup[-1]]
        self.show()
    
    def rm_popup(self,seq_popup_name):
        if seq_popup_name in self.list_popup:
            self.state = self.seq[self.timeline]
            self.list_popup.remove(seq_popup_name)
            print("sup de popup : {}",self.list_popup)
            if len(self.list_popup) != 0:
                self.state = self.seq_popup[self.list_popup[-1]]
            self.show()

