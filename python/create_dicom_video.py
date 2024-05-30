import pydicom.uid
from pydicom import Dataset, FileDataset, dcmwrite
from pydicom.dataset import FileMetaDataset
from pydicom.encaps import encapsulate
from pydicom.tag import Tag
import cv2
import tempfile
import orthanc
import json
from pprint import pprint

class CreateDicomVideo:
    def __init__(self, byte: bytes):
        self.bytes: bytes = byte
        self.dataset: Dataset
        self.fileDataset: FileDataset

    def save_bytes(self, output) -> None:
        with open(output, 'wb') as f:
            f.write(self.bytes)

    def save_dicom(self, output) -> None:
        dcmwrite(output, self.fileDataset, write_like_original=False)

    def _bytes_to_video_capture(self) -> cv2.VideoCapture:
        with tempfile.NamedTemporaryFile() as f:
            f.write(self.bytes)
            video_stream = cv2.VideoCapture(f.name)
            return video_stream
        
    def _retrieve_level_from_orthancid(self, orthanc_id: str) -> str | None: # there's no built-in orthanc function to retrieve the level of an orthanc id
        try: # Check if it is a patient
            json.loads(orthanc.RestApiGet(f"/patients/{orthanc_id}/"))
            return 'patients'
        except:
            pass
        try: # Check if it is a study
            json.loads(orthanc.RestApiGet(f"/studies/{orthanc_id}/"))
            return 'studies'
        except:
            pass
        try: # Check if it is a series
            json.loads(orthanc.RestApiGet(f"/series/{orthanc_id}/"))
            return 'series'
        except:
            pass
        return None # None of the above
    
    def _retrieve_dicom_data(self, orthanc_id: str) -> dict:
        level = self._retrieve_level_from_orthancid(orthanc_id)
        data = {}
        if level == 'series':
            data_series = json.loads(orthanc.RestApiGet(f"/series/{orthanc_id}/"))
            data = {
                'SeriesInstanceUID': data.get('MainDicomTags', {}).get('SeriesInstanceUID'),
                'SeriesDescription': data.get('MainDicomTags', {}).get('SeriesDescription'),
                'SeriesDate': data.get('MainDicomTags', {}).get('SeriesDate'),
                'SeriesTime': data.get('MainDicomTags', {}).get('SeriesTime'),
            }
            orthanc_id = data_series.get('ParentStudy')
        if level == 'studies' or level == 'series':
            data_studies = json.loads(orthanc.RestApiGet(f"/studies/{orthanc_id}/"))
            data.update({
                'StudyInstanceUID': data_studies.get('MainDicomTags', {}).get('StudyInstanceUID'),
                'AccessionNumber': data_studies.get('MainDicomTags', {}).get('AccessionNumber'),
                'StudyDate': data_studies.get('MainDicomTags', {}).get('StudyDate'),
                'StudyTime': data_studies.get('MainDicomTags', {}).get('StudyTime'),
                'StudyDescription': data_studies.get('MainDicomTags', {}).get('StudyDescription'),
                'StudyID': data_studies.get('MainDicomTags', {}).get('StudyID'),
            })
            orthanc_id = data_studies.get('ParentPatient')
        if level == 'patients' or level == 'studies' or level == 'series':
            data_patient = json.loads(orthanc.RestApiGet(f"/patients/{orthanc_id}/"))
            data.update({
                'PatientName': data_patient.get('MainDicomTags', {}).get('PatientName'),
                'PatientID': data_patient.get('MainDicomTags', {}).get('PatientID'),
                'PatientBirthDate': data_patient.get('MainDicomTags', {}).get('PatientBirthDate'),
                'PatientSex': data_patient.get('MainDicomTags', {}).get('PatientSex'),
            })
        return data

    def create_dicom(self, parent: str, dcm_data: dict) -> 'CreateDicomVideo':
        parent_data = self._retrieve_dicom_data(parent)
        self.dataset = Dataset()

        self.dataset.PatientName = parent_data.get('PatientName', "<PATIENT_NAME>")
        self.dataset.PatientID = parent_data.get('PatientID', "<PATIENT_ID>")
        self.dataset.PatientBirthDate = parent_data.get('PatientBirthDate', None)
        self.dataset.PatientSex = parent_data.get('PatientSex', None)
        
        self.dataset.StudyInstanceUID = parent_data.get('StudyInstanceUID', pydicom.uid.generate_uid())
        self.dataset.AccessionNumber = parent_data.get('AccessionNumber', "")
        self.dataset.StudyDate = parent_data.get('StudyDate', "")
        self.dataset.StudyTime = parent_data.get('StudyTime', "")
        self.dataset.StudyDescription = parent_data.get('StudyDescription', "Video")
        self.dataset.StudyID = parent_data.get('StudyID', parent_data.get('StudyID', ""))
        
        self.dataset.SeriesInstanceUID = parent_data.get('SeriesInstanceUID', pydicom.uid.generate_uid())
        self.dataset.SeriesDescription = parent_data.get('SeriesDescription', None)
        self.dataset.SeriesDate = parent_data.get('SeriesDate', None)
        self.dataset.SeriesTime = parent_data.get('SeriesTime', None)
        
        self.dataset.SOPClassUID = pydicom.uid.VideoPhotographicImageStorage
        self.dataset.PhotometricInterpretation = "YBR_PARTIAL_420"
        self.dataset.SpecificCharacterSet = 'ISO_IR 100'
        self.dataset.ImageType = ['DERIVED', 'SECONDARY']
        self.dataset.InstanceCreatorUID = pydicom.uid.PYDICOM_IMPLEMENTATION_UID
        self.dataset.SOPInstanceUID = pydicom.uid.generate_uid()
        self.dataset.Modality = "OT"
        self.dataset.ConversionType = "DV"
        self.dataset.Manufacturer = ""
        self.dataset.ReferringPhysicianName = ""
        self.dataset.SeriesNumber = ""
        self.dataset.PatientOrientation = ""
        self.dataset.Laterality = ""
        self.dataset.InstanceNumber = 1
        self.dataset.SamplesPerPixel = 3
        self.dataset.PlanarConfiguration = 0
        self.dataset.FrameIncrementPointer = Tag("FrameTime")
        self.dataset.BitsAllocated = 8
        self.dataset.HighBit = 7
        self.dataset.PixelRepresentation = 0
        self.dataset.BitsStored = 8

        self.dataset.PixelData = encapsulate([self.bytes])

        video_cap = self._bytes_to_video_capture()

        self.dataset.NumberOfFrames = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.dataset.Rows = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.dataset.Columns = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.dataset.CineRate = int(video_cap.get(cv2.CAP_PROP_FPS))
        self.dataset.FrameTime = 1 / self.dataset.CineRate * 1000
        
        self.dataset.update(dcm_data)

        fileMetaDataset = FileMetaDataset()
        fileMetaDataset.TransferSyntaxUID = pydicom.uid.MPEG4HP41BD
        fileMetaDataset.MediaStorageSOPClassUID = pydicom.uid.VideoEndoscopicImageStorage
        fileMetaDataset.ImplementationClassUID = pydicom.uid.PYDICOM_IMPLEMENTATION_UID
        fileMetaDataset.MediaStorageSOPInstanceUID = self.dataset.SOPInstanceUID

        file_name = f"{dcm_data.get('PatientID', '0')}_{dcm_data.get('StudyID', '0')}_{dcm_data.get('AccessionNumber', '0')}.dcm"

        self.fileDataset = FileDataset(file_name, self.dataset, None, fileMetaDataset, False, True)

        return self