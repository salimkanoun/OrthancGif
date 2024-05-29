import pydicom.uid
from pydicom import Dataset, FileDataset, dcmwrite
from pydicom.dataset import FileMetaDataset
from pydicom.encaps import encapsulate
from pydicom.tag import Tag

import cv2




class CreateDicomVideo:
    def __init__(self, filename: str):
        self.filename = filename

    def create_dicom(self, output) -> None:
        ds = Dataset()
        ds.SeriesDescription = "Video"
        ds.StudyDescription = "Video"
        ds.PatientName = "CITIZEN^Joan"
        ds.PhotometricInterpretation = 'YBR_PARTIAL_420'
        ds.LossyImageCompression = '01'
        ds.PatientID = "123456"
        ds.StudyInstanceUID = pydicom.uid.generate_uid()
        ds.SeriesInstanceUID = pydicom.uid.generate_uid()
        ds.SOPInstanceUID = pydicom.uid.generate_uid()
        ds.SOPClassUID = pydicom.uid.VideoEndoscopicImageStorage
        ds.SpecificCharacterSet = 'ISO_IR 100'
        ds.ImageType = ['DERIVED', 'SECONDARY']
        ds.InstanceCreatorUID = pydicom.uid.PYDICOM_IMPLEMENTATION_UID
        ds.StudyDate = "20200101"
        ds.SeriesDate = "20200101"
        ds.StudyTime = "000000.000"
        ds.SeriesTime = "000000.000"
        ds.AccessionNumber = "123456"
        ds.Modality = "ES"
        ds.ConversionType = "DV"
        ds.Manufacturer = "GaelO"
        ds.InstitutionName = "GaelO"
        ds.ReferringPhysicianName = ""
        ds.PatientBirthDate = "20200101"
        ds.PatientSex = "F"
        ds.StudyID = "123456"
        ds.SeriesNumber = 1
        ds.InstanceNumber = 1
        ds.PatientOrientation = ""
        ds.Laterality = ""
        ds.SamplesPerPixel = 3
        ds.PlanarConfiguration = 0
        ds.FrameIncrementPointer = Tag("FrameTime")
        ds.BitsAllocated = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.BitsStored = 8
        
        with open(self.filename, 'rb') as f:
            video = cv2.VideoCapture(self.filename)

            ds.PixelData = encapsulate([f.read()])
            ds.NumberOfFrames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            ds.Rows= int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            ds.Columns = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            ds.CineRate = int(video.get(cv2.CAP_PROP_FPS))
            ds.FrameTime = 1 / ds.CineRate * 1000
            
        file_meta = FileMetaDataset()
        file_meta.TransferSyntaxUID = pydicom.uid.MPEG4HP41BD
        file_meta.MediaStorageSOPClassUID = pydicom.uid.VideoEndoscopicImageStorage
        file_meta.ImplementationClassUID = pydicom.uid.PYDICOM_IMPLEMENTATION_UID
        file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
        file_dataset = FileDataset(output, ds, None, file_meta, False, True)
        dcmwrite(output, file_dataset, write_like_original=False)

if __name__ == '__main__':
    create_video = CreateDicomVideo("c6e40975-a3be-e9a6-36ab-09e678c9f095.mp4")
    # create_video = CreateDicomVideo("file_example_MP4_1920_18MG.mp4")
    create_video.create_dicom("video.dcm")
