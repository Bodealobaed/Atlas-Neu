"""Official research dataset pointers. Nothing is scraped or downloaded implicitly."""
DATASETS = {
    'chest': {'name':'MedMNIST ChestMNIST', 'url':'https://medmnist.com/v2', 'dataset_id':'chestmnist', 'purpose':'14-label chest X-ray research benchmark'},
    'bone': {'name':'MedMNIST Organ/Fracture datasets', 'url':'https://medmnist.com/v2', 'dataset_id':'fracturemnist3d', 'purpose':'3D fracture research benchmark'},
    'brain': {'name':'MedMNIST VesselMNIST3D', 'url':'https://medmnist.com/v2', 'dataset_id':'vesselmnist3d', 'purpose':'brain MRA vessel-shape benchmark'},
    'cardiac': {'name':'The Cancer Imaging Archive catalog', 'url':'https://www.cancerimagingarchive.net/browse-data/', 'dataset_id':None, 'purpose':'browse task-specific licensed imaging collections'},
}

def catalog():
    return {k:dict(v) for k,v in DATASETS.items()}
