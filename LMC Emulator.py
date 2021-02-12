import re
import tkinter as tk


class LMC:
    def __init__(self):
        self.COMMANDS = {"LDA": "5xx",  # Loads the value of mailbox xx
                         "STA": "3xx",  # Stores contents of the ACC in mailbox xx
                         "ADD": "1xx",  # Adds the value of whatever is in mailbox xx to the ACC
                         "SUB": "2xx",  # Subtracts the value of whatever is in mailbox xx from the ACC
                         "INP": "901",  # Goto the INBOX,  fetch the value from the user and put it in the ACC
                         "OUT": "902",  # Copy the value from the accumulator to the OUTBOX
                         "HLT": "000",  # Stop the program
                         "BRZ": "7xx",  # If the ACC is 000, set the PC to the value xx.
                         "BRP": "8xx",  # If the ACC is >=0, seth the PC to the value xx.
                         "BRA": "6aa",  # Set the PC to the value xx.
                         "DAT": "xxx"}  # Stores the value in the next available mailbox
        self.MEMORY = ["000" for i in range(0, 100)]

        # Registers
        self.PC = 0
        self.IR = 0
        self.AD = 0
        self.ACC = 0

        # Creating UI
        # Creating textbox/scrollbar
        self.root = tk.Tk()
        self.root.geometry("925x800")
        self.root.resizable(height=None, width=None)

        self.inst_frame = tk.Frame(self.root)
        self.sb = tk.Scrollbar(self.inst_frame)
        self.text_box = tk.Text(self.inst_frame)
        self.sb.config(command=self.text_box.yview)
        self.text_box.config(yscrollcommand=self.sb.set)
        self.sb.grid(row=0, column=1)
        self.text_box.grid(row=0, column=0, sticky='ns')
        self.text_box.insert(tk.END, "Enter your instructions here:")
        self.inst_frame.grid(row=0, column=0, sticky="nsew")

        # Creating RUN, STOP and log
        self.rsl_frame = tk.Frame(self.root)
        self.log = tk.Text(self.rsl_frame)
        self.log.insert(tk.END, "~~~ START OF LOG ~~~")
        self.log.config(state="disabled")
        self.log_sb = tk.Scrollbar(self.rsl_frame)
        self.log_sb.config(command=self.log.yview)
        self.log.config(yscrollcommand=self.log_sb.set)
        self.log.grid(row=0, column=0)
        self.log_sb.grid(row=0, column=1)
        self.rsl_frame.grid(row=1, column=0)

        self.button_frame = tk.Frame(self.root)
        self.var = tk.IntVar()
        self.run = tk.Button(self.button_frame, text="RUN", command=self.run_instructions)
        self.compileB = tk.Button(self.button_frame, text="COMPILE", command=self.compile)
        self.entryB = tk.Entry(self.button_frame, text="Enter your number")
        self.submit = tk.Button(self.button_frame, text="SUBMIT", command=self.done_wait)
        self.run.grid(row=0, column=0)
        self.compileB.grid(row=0, column=1)
        self.submit.grid(row=0, column=2)
        self.entryB.grid(row=0, column=3)
        self.button_frame.grid(row=2, column=0)

        # Creating the labels for ACC, PC, AD AND IR
        self.CPU_frame = tk.Frame(self.root)
        self.ACCL = tk.Label(self.CPU_frame, text="Accumulator: ")
        self.PCL = tk.Label(self.CPU_frame, text="Program Counter: ")
        self.ADL = tk.Label(self.CPU_frame, text="Address Register: ")
        self.IRL = tk.Label(self.CPU_frame, text="Instruction Register: ")
        self.ACCL.grid(row=0, column=0)
        self.PCL.grid(row=1, column=0)
        self.IRL.grid(row=2, column=0)
        self.ADL.grid(row=2, column=1)
        self.CPU_frame.grid(row=0, column=1)

        # Creating labels for memory
        self.memory_labels = []
        self.memory_frame = tk.Frame(self.root)
        r = 0
        c = 0
        for i in range(0, 100):
            self.memory_labels.append(tk.Label(self.memory_frame, text="000"))
            self.memory_labels[i].grid(row=r, column=c)
            c += 1
            if (i+1) % 10 == 0:
                r += 1
                c = 0
        self.memory_frame.grid(row=1, column=1)
        self.root.mainloop()

    def done_wait(self):
        temp = self.entryB.get()
        print(temp)
        self.var.set(temp)

    def compile(self):
        # Converting instructions and placing them in memory
        # Finding any commands with DAT
        instructions = self.text_box.get("1.0", "end-1c").split("\n")
        print(instructions)
        x = 0
        for item in instructions:
            if len(item) > 3:
                item = item.split(" ")
            if item[1] == "DAT":
                var = item[0]  # Finding the name of the variable
                instructions[x] = "DAT 000"  # Replacing instruction

                y = 0
                for item in instructions:
                    if len(item) > 3:
                        item = item.replace(var, str(x))
                        instructions[y] = item
                    y += 1
            x += 1
        # Finding all the positions
        for item in enumerate(instructions):
            if len(item[1]) > 3:
                if item[1][:3] == "DAT":
                    inst = item[1][4:]
                else:
                    inst = self.COMMANDS[item[1][:3]][0] + item[1][4:]
            else:
                inst = self.COMMANDS[item[1]]
            self.MEMORY[item[0]] = inst
            self.memory_labels[item[0]]["text"] = inst
        self.log.config(state="normal")
        self.log.insert(tk.END, f"\nTranslated instructions: {instructions}")
        self.log.config(state="disabled")

    def run_instructions(self):
        # Fetch
        self.log.config(state="normal")
        self.log.insert(tk.END, f"\nFetching Instruction {self.PC}...")
        self.log.config(state="disabled")
        self.IR = int(self.MEMORY[self.PC][0])
        self.AD = int(self.MEMORY[self.PC][1:])
        self.PC += 1
        self.IRL["text"] = f"Instruction Register: {self.IR}"
        self.ADL["text"] = f"Address Register: {self.AD}"
        self.PCL["text"] = f"Program Counter: {self.PC}"

        # Decode/Execute
        self.log.config(state="normal")
        self.log.insert(tk.END, "\nDecoding")
        self.log.config(state="disabled")
        if self.IR == 0:
            self.PC = -1
            self.log.config(state="normal")
            self.log.insert(tk.END, "\n~~~ END OF LOG ~~~")
            self.log.config(state="disabled")
        elif self.IR == 1:
            self.log.config(state="normal")
            self.log.insert(tk.END, "\nAdding to ACC...")
            self.log.config(state="disabled")
            self.ACC += self.MEMORY[self.AD]
            self.ACCL["text"] = f"Accumulator: {self.ACC}"

        elif self.IR == 2:
            self.log.config(state="normal")
            self.log.insert(tk.END, "\nTaking away from ACC...")
            self.log.config(state="disabled")
            self.ACC -= self.MEMORY[self.AD]
            self.ACCL["text"] = f"Accumulator: {self.ACC}"

        elif self.IR == 3:
            self.log.config(state="normal")
            self.log.insert(tk.END, f"\nSetting Memory location {self.AD} equal to ACC...")
            self.log.config(state="disabled")
            self.MEMORY[self.AD] = self.ACC
            self.memory_labels[self.AD]["text"] = self.ACC

        elif self.IR == 5:
            self.log.config(state="normal")
            self.log.insert(tk.END, f"\nSetting ACC equal to Memory location {self.AD}...")
            self.log.config(state="disabled")
            self.ACC = self.MEMORY[self.AD]
            self.ACCL["text"] = f"Accumulator: {self.ACC}"

        elif self.IR == 6:
            self.log.config(state="normal")
            self.log.insert(tk.END, f"\nGoing to instruction at Memory location {self.AD}...")
            self.log.config(state="disabled")
            self.PC = self.MEMORY[self.AD]
        elif self.IR == 7:
            if self.ACC == 0:
                self.log.config(state="normal")
                self.log.insert(tk.END, f"\nGoing to instruction at Memory location {self.AD}...")
                self.log.config(state="disabled")
                self.PC = self.MEMORY[self.AD]
        elif self.IR == 8:
            if self.ACC >= 0:
                self.log.config(state="normal")
                self.log.insert(tk.END, f"\nGoing to instruction at Memory location {self.AD}...")
                self.log.config(state="disabled")
                self.PC = self.MEMORY[self.AD]
        elif self.IR == 9:
            if self.AD == 1:
                self.log.config(state="normal")
                self.log.insert(tk.END, "\nGetting an Input...")
                self.log.config(state="disabled")
                self.submit.wait_variable(self.var)
                self.ACC = self.var.get()
                self.ACCL["text"] = f"Accumulator: {self.ACC}"
            else:
                self.log.config(state="normal")
                self.log.insert(tk.END, "\nDisplaying the value of ACC...")
                self.log.insert(tk.END, f"\nValue of ACC: {self.ACC}")
                self.log.config(state="disabled")
        if self.PC != -1:
            self.root.after(100, self.run_instructions)


instruction = """INP
STA FIRST
INP
ADD FIRST
OUT
INP
SUB FIRST
OUT
HLT
FIRST DAT"""
LMC_inst = LMC()
LMC_inst.compile()
LMC_inst.run_instructions()

