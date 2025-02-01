import random

defaultNeuronStartStrength = 1

#create neuron object
class Neuron:
    def __init__(self, name):
        self.name = name
        self.connections = []
        self.strengths = []
    
    def connect(self, Neuron):
        self.connections.append(Neuron)
        self.strengths.append(defaultNeuronStartStrength)
    
    def getTheStrengthTo(self, Neuron):
        if Neuron in self.connections:
            return self.strengths[self.connections.index(Neuron)]
        else:
            return 0
    
    def __str__(self):
        return f"Neuron({self.name})"

firstNeuron     = Neuron("1")
secondNeuron    = Neuron("2")
thirdNeuron     = Neuron("3")

firstNeuron.connect(secondNeuron)
secondNeuron.connect(thirdNeuron)

# Jumper: Is the focus on specific neurons.

class Jumper:
    """
    The Jumper class is responsible for jumping between neurons in the brain.
    Every time tick it jumps to another neuron, depending on the following logic:
    - Every jump costs energy, depending on the strength of the connection. The stronger the connection, the less energy it costs.
    - It looks how much energy it has left.
    - It looks how much energy the jump would cost.
    - A neuron can either explore with less energy, stay at the current neuron or jump back to a neuron with a stronger connection.
    - The decision is based on the energy and the strength of the connection. If multiple options are possible randomly choose one.
    - When it jumps over to another neuron it will increase the strength of the connection and so decrease the energy cost when it jumps over it next time. But it will also cost energy as high as the strength of the connection (when the connection is lower than the energy level, it will cost the energy level). If not, it will only cost 1 energy.
    """
    def __init__(self, Neuron):
        self.currentNeuron = Neuron
        self.energy = 100

    
    def jumpToThis(self, DestinationNeuron):
        # check if the neuron is in the possible jumps
        if DestinationNeuron in self.currentNeuron.connections:
            # check if the energy is enough
            energyCostToJumpToThisNewNeuron = self.currentNeuron.getTheStrengthTo(DestinationNeuron)
            if energyCostToJumpToThisNewNeuron <= self.energy:    
                # increase the strength of the connection between origin and destination Neuron
                self.currentNeuron.strengths[self.currentNeuron.connections.index(DestinationNeuron)] += energyCostToJumpToThisNewNeuron
                # decrease the energy
                self.energy -= energyCostToJumpToThisNewNeuron
                # jump to the new neuron
                print(f"Jumping from {self.currentNeuron} to {DestinationNeuron} with energy cost {energyCostToJumpToThisNewNeuron}. Remaining energy: {self.energy}")
                self.currentNeuron = DestinationNeuron
            else:
                #increase strength of the connection by one
                self.currentNeuron.strengths[self.currentNeuron.connections.index(DestinationNeuron)] += 1
                # decrease the energy by only one
                self.energy -= 1
                # jump to the new neuron
                print(f"Jumping from {self.currentNeuron} to {DestinationNeuron} with energy cost 1. Remaining energy: {self.energy}")
                self.currentNeuron = DestinationNeuron
                


    def start(self):
        while self.energy > 0:
            # check energy level
            energy = self.energy

            # check possible jumps
            possibleJumps = []
            for possibleJump in self.currentNeuron.connections:
                if self.currentNeuron.getTheStrengthTo(possibleJump) <= energy:
                    possibleJumps.append(possibleJump)
            
            # check if there are possible jumps
            if len(possibleJumps) == 0:
                print("No possible jumps. Stopping.")
                self.energy += 1
                return
            
            if len(possibleJumps) == 1:
                print(f"Only one possible jump to {possibleJumps[0]}")
                self.jumpToThis(possibleJumps[0])

            if len(possibleJumps) > 1:
                length = len(possibleJumps)
                #choose random between the possible jumps
                randomJump = possibleJumps[random.randint(0, length-1)]
                print(f"Multiple possible jumps. Randomly jumping to {randomJump}")
                self.jumpToThis(randomJump)

# Example usage
jumper = Jumper(firstNeuron)        
jumper.start()
