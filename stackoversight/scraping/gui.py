# # For gui
# from tkinter import *
#
# # TODO: setup as queue of parent links that this thread will continuously process
# root = Tk()
#
# # TODO: show list of processed and to be processed links in this frame
# processing_frame = Frame(root)
#
# to_be_processed_label = Label(processing_frame, text="Links to be processed")
# has_been_processed_label = Label(processing_frame, text="Links that have been processed")
#
# to_be_processed_label.grid(row=0, column=0)
# has_been_processed_label.grid(row=0, column=1)
#
# processing_frame.pack(side=BOTTOM)
#
# # TODO: have all the configurable fields able to be set here
# link_generation_frame = Frame(root)
#
# # parent_link_entry = Entry(root)
#
# fields = []
# for field in site.fields:
#     var = StringVar()
#     label = Label(link_generation_frame, text=field.capitalize())
#     entry = Entry(link_generation_frame, textvariable=var)
#
#     label.grid(row=len(fields), column=0)
#     entry.grid(row=len(fields), column=1)
#
#     fields.append((field, var, label, entry))
#
# link_generation_frame.pack(side=TOP)
#
# root.mainloop()
