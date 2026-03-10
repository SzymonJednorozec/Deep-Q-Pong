import torch
import torch.onnx
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os
import copy
import numpy as np

class Linear_Qnet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size,hidden_size)
        self.linear2 = nn.Linear(hidden_size,output_size)

    def forward(self,x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x
    
    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

    def save_onnx(self, file_name='model.onnx'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        
        file_path = os.path.join(model_folder_path, file_name)
        
        self.eval() 
        
        dummy_input = torch.randn(1, self.linear1.in_features)
        
        try:
            torch.onnx.export(
                self,
                dummy_input,
                file_path,
                export_params=True,
                opset_version=18,  
                do_constant_folding=True,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
            )
        except Exception as e:
            print(f"Błąd eksportu: {e}")
        finally:
            self.train()
    


class Qtrainer:
    def __init__(self,model,lr,gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.target_model = copy.deepcopy(model)
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()
    
    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(np.array(state), dtype=torch.float)
        next_state = torch.tensor(np.array(next_state), dtype=torch.float)
        action = torch.tensor(np.array(action), dtype=torch.long)
        reward = torch.tensor(np.array(reward), dtype=torch.float)
        done = torch.tensor(np.array(done), dtype=torch.bool)

        pred = self.model(state)
        target = pred.clone()

        with torch.no_grad():
            next_q_values = self.target_model(next_state)
            max_next_q = torch.max(next_q_values, dim=1)[0]
        
        # Równanie Bellmana w jednej linii!
        Q_new = reward + self.gamma * max_next_q * (~done)

        action_indices = torch.argmax(action, dim=1)
        target[range(len(target)), action_indices] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()


        
