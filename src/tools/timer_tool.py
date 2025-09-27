"""
Timer management tool for setting and managing timers.
"""

import re
import time
import threading
import platform
import subprocess
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun


class TimerTool(BaseTool):
    """LangChain tool for timer operations."""
    
    name = "timer_manager"
    description = "Set timers. Input should be duration in seconds or descriptive text like '5 minutes'."
    
    def __init__(self):
        super().__init__()
        self.active_timers = {}
        self.timer_counter = 0
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Set a timer."""
        try:
            duration = self._parse_duration(query)
            self.timer_counter += 1
            timer_id = self.timer_counter
            
            # Format time string
            time_str = self._format_duration(duration)
            
            def timer_thread():
                time.sleep(duration)
                if timer_id in self.active_timers:
                    print(f"\n⏰ TIMER COMPLETE! Your {time_str} timer is done!")
                    # System notification
                    try:
                        if platform.system() == "Windows":
                            subprocess.run(['msg', '*', f'Jarvis: Timer for {time_str} complete!'])
                        elif platform.system() == "Darwin":
                            subprocess.run(['osascript', '-e', f'display notification "Timer complete!" with title "Jarvis - {time_str}"'])
                        elif platform.system() == "Linux":
                            subprocess.run(['notify-send', 'Jarvis Timer', f'{time_str} complete!'])
                    except:
                        pass
                    del self.active_timers[timer_id]
            
            self.active_timers[timer_id] = threading.Thread(target=timer_thread)
            self.active_timers[timer_id].daemon = True
            self.active_timers[timer_id].start()
            
            return f"Timer set for {time_str}. I'll notify you when it's done!"
            
        except Exception as e:
            return f"Timer setup failed: {str(e)}"
    
    def _parse_duration(self, text):
        """Parse duration from text."""
        patterns = [
            (r'(\d+)\s*(?:minutes?|mins?)', lambda x: int(x) * 60),
            (r'(\d+)\s*(?:seconds?|secs?)', lambda x: int(x)),
            (r'(\d+)\s*(?:hours?|hrs?)', lambda x: int(x) * 3600),
        ]
        
        for pattern, converter in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return converter(match.group(1))
        
        # Try to extract just numbers
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0]) * 60  # Default to minutes
        
        return 60  # Default 1 minute
    
    def _format_duration(self, duration):
        """Format duration as readable string."""
        if duration >= 3600:
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            return f"{hours} hour{'s' if hours != 1 else ''}" + (f" {minutes} min" if minutes else "")
        elif duration >= 60:
            minutes = duration // 60
            seconds = duration % 60
            return f"{minutes} minute{'s' if minutes != 1 else ''}" + (f" {seconds} sec" if seconds else "")
        else:
            return f"{duration} second{'s' if duration != 1 else ''}"