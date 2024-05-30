import pydicom

filepath = "video3.dcm"

ds = pydicom.dcmread(filepath)
print(ds)