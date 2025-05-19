import time

class Tween:
    # Animation easing functions
    @staticmethod
    def linear(amount):
        return amount
    
    @staticmethod
    def quad_in_out(amount):
        if (amount * 2) < 1:
            return 0.5 * amount * amount
        amount -= 1
        return -0.5 * (amount * (amount - 2) - 1)
    
    @staticmethod
    def quad_out(amount):
        return amount * (2 - amount)
    
    @staticmethod
    def no_easing(_):
        return 1
    
    def __init__(self, start):
        self.start = start
        self.value = start.copy()
        self.steps = []
        self.loop_enabled = False
        self.duration = 0
    
    def to(self, value, duration, easing):
        prev_step = self.steps[-1] if self.steps else None
        starts_at = prev_step['ends_at'] if prev_step else 0
        ends_at = starts_at + duration
        from_val = prev_step['to'] if prev_step else self.start.copy()
        
        step = {
            'from': from_val,
            'to': value,
            'starts_at': starts_at,
            'ends_at': ends_at,
            'duration': duration,
            'easing': easing
        }
        
        self.steps.append(step)
        self.duration += duration
        return self
    
    def wait(self, duration):
        prev_step = self.steps[-1] if self.steps else None
        starts_at = prev_step['ends_at'] if prev_step else 0
        ends_at = starts_at + duration
        value = prev_step['to'] if prev_step else self.start.copy()
        
        step = {
            'from': value.copy(),
            'to': value.copy(),
            'starts_at': starts_at,
            'ends_at': ends_at,
            'duration': duration,
            'easing': self.no_easing
        }
        
        self.steps.append(step)
        self.duration += duration
        return self
    
    def loop(self):
        self.loop_enabled = True
        return self
    
    def set(self, current_time):
        if current_time < 0:
            current_time = 0
            
        if self.loop_enabled:
            current_time = current_time % self.duration
        
        step = None
        for _step in self.steps:
            if current_time >= _step['starts_at']:
                step = _step
        
        if not step:
            print(f"Warning: no step for time {current_time}")
            return
        
        alpha = (current_time - step['starts_at']) / step['duration']
        if alpha > 1:
            alpha = 1
            
        ease = step['easing'](alpha)
        
        for key in step['to']:
            self.value[key] = step['from'][key] + ((step['to'][key] - step['from'][key]) * ease)
