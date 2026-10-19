"""Opt-in reproducible research training on official MedMNIST splits.

Requires: pip install medmnist torch scikit-learn
Run: python train_medmnist_research.py --dataset pneumoniamnist --epochs 3 --output results.json
No training occurs inside Streamlit; this does not deploy a clinical model.
"""
import argparse
import json
from pathlib import Path

def train(dataset='pneumoniamnist', epochs=3, output='results.json'):
    import numpy as np
    import medmnist
    import torch
    from sklearn.metrics import accuracy_score, roc_auc_score
    from torch import nn
    from torch.utils.data import DataLoader
    from torchvision import transforms
    if dataset not in {'pneumoniamnist','breastmnist','organamnist','organcmnist','organsmnist'}:
        raise ValueError('Choose a supported 2D MedMNIST benchmark.')
    torch.manual_seed(42)
    info=medmnist.INFO[dataset]
    cls=getattr(medmnist,info['python_class'])
    transform=transforms.Compose([transforms.ToTensor()])
    loaders={split:DataLoader(cls(split=split,transform=transform,download=True),batch_size=64,shuffle=split=='train') for split in ('train','val','test')}
    channels=int(info['n_channels']); classes=len(info['label'])
    net=nn.Sequential(nn.Conv2d(channels,16,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),nn.Conv2d(16,32,3,padding=1),nn.ReLU(),nn.AdaptiveAvgPool2d(1),nn.Flatten(),nn.Linear(32,classes))
    opt=torch.optim.Adam(net.parameters(),lr=0.001)
    loss_fn=nn.CrossEntropyLoss()
    def evaluate(split):
        net.eval(); ys=[]; ps=[]
        with torch.no_grad():
            for x,y in loaders[split]:
                logits=net(x); ps.extend(torch.softmax(logits,dim=1).numpy().tolist()); ys.extend(y.view(-1).tolist())
        preds=np.asarray(ps); truth=np.asarray(ys)
        result={'accuracy':float(accuracy_score(truth,preds.argmax(1))), 'samples':int(len(truth))}
        if classes==2 and len(set(truth))==2: result['auc']=float(roc_auc_score(truth,preds[:,1]))
        return result
    best=-1; best_state=None
    for _ in range(epochs):
        net.train()
        for x,y in loaders['train']:
            opt.zero_grad(); loss=loss_fn(net(x),y.view(-1).long()); loss.backward(); opt.step()
        score=evaluate('val')['accuracy']
        if score>best:
            best=score; best_state={k:v.detach().clone() for k,v in net.state_dict().items()}
    net.load_state_dict(best_state)
    result={'dataset':dataset,'validation':evaluate('val'),'test':evaluate('test'),'epochs':epochs,
            'intended_use':'Research benchmark only; not a clinical diagnosis or deployment-ready model',
            'source':'https://medmnist.com/v2'}
    Path(output).write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset',default='pneumoniamnist');p.add_argument('--epochs',type=int,default=3);p.add_argument('--output',default='results.json')
    a=p.parse_args();print(train(a.dataset,a.epochs,a.output))
