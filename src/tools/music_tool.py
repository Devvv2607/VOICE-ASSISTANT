"""
Music playback tool for playing music on various platforms.
"""

import json
import webbrowser
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun


class MusicTool(BaseTool):
    """LangChain tool for music operations."""
    
    name = "music_player"
    description = "Play music on various platforms. Input should be JSON with 'song' and 'platform' (spotify/youtube/apple)."
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Play music."""
        try:
            if query.startswith('{'):
                params = json.loads(query)
                song = params.get('song', 'music')
                platform = params.get('platform', 'youtube')
            else:
                song = query
                platform = 'youtube'
            
            music_platforms = {
                'spotify': f'https://open.spotify.com/search/{song.replace(" ", "%20")}',
                'youtube': f'https://www.youtube.com/results?search_query={song.replace(" ", "+")}',
                'apple': f'https://music.apple.com/search?term={song.replace(" ", "+")}'
            }
            
            url = music_platforms.get(platform, music_platforms['youtube'])
            webbrowser.open(url)
            
            return f"Opening '{song}' on {platform.title()}"
            
        except Exception as e:
            return f"Music playback failed: {str(e)}"