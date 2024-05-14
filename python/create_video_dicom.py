import pydicom.uid
from pydicom import Dataset, FileDataset, dcmwrite
from pydicom.dataset import FileMetaDataset
from pydicom.encaps import encapsulate
from pydicom.tag import Tag




class CreateDicomVideo:
    def __init__(self, filename: str):
        self.filename = filename

    def create_dicom(self, output) -> None:
        ds = Dataset()
        ds.PatientName = "CITIZEN^Joan"
        ds.PhotometricInterpretation = 'YBR_PARTIAL_420'
        ds.LossyImageCompressionMethod = 'ISO_14496_10'
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
        
        ds.NumberOfFrames = 100
        ds.Rows= 1080
        ds.Columns = 1920
        ds.FrameTime = 0.033
                
        with open(self.filename, 'rb') as f:
            ds.PixelData = encapsulate([f.read()])
            
        file_meta = FileMetaDataset()
        file_meta.TransferSyntaxUID = pydicom.uid.MPEG4HP41
        file_meta.MediaStorageSOPClassUID = pydicom.uid.VideoEndoscopicImageStorage
        file_meta.ImplementationClassUID = pydicom.uid.PYDICOM_IMPLEMENTATION_UID    
        file_dataset = FileDataset('video.dcm', ds, None, file_meta, False, True)
        dcmwrite('video.dcm',file_dataset)

if __name__ == '__main__':
    create_video = CreateDicomVideo("c6e40975-a3be-e9a6-36ab-09e678c9f095.mp4")
    create_video.create_dicom("video.dcm")
