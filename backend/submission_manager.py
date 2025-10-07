"""
Submission Manager - Handles batch form submission with pause/resume/kill controls.
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import time
from form_automation import FormAutomation
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SubmissionManager:
    """Manages batch form submission state and execution."""
    
    def __init__(self):
        """Initialize submission manager with idle state."""
        self.state = {
            'status': 'idle',  # idle/running/paused/completed/killed
            'current_position': 0,
            'total': 0,
            'completed': 0,
            'failed': 0,
            'start_time': None,
            'elapsed_seconds': 0,
            'log': [],
            'errors': []
        }
        self.url: Optional[str] = None
        self.students: List[Dict] = []
        self.automation: Optional[FormAutomation] = None
        self.task: Optional[asyncio.Task] = None
        self._should_stop = False
        self._should_pause = False
    
    def get_status(self) -> Dict:
        """
        Get current submission status.
        
        Returns:
            Dictionary with current state including progress, logs, and errors
        """
        # Calculate elapsed time if running
        if self.state['status'] == 'running' and self.state['start_time']:
            self.state['elapsed_seconds'] = int(time.time() - self.state['start_time'])
        
        return {
            'completed': self.state['completed'],
            'total': self.state['total'],
            'elapsed_seconds': self.state['elapsed_seconds'],
            'status': self.state['status'],
            'current_position': self.state['current_position'],
            'failed': self.state['failed'],
            'log': self.state['log'],
            'errors': self.state['errors']
        }
    
    async def start_submission(self, url: str, students: List[Dict]) -> Dict:
        """
        Start batch form submission.
        
        Args:
            url: Target form URL
            students: List of student data dictionaries with row_number and data
        
        Returns:
            Dictionary with job status
        """
        if self.state['status'] == 'running':
            raise Exception("Submission already running")
        
        # Initialize state
        self.url = url
        self.students = students
        self.state = {
            'status': 'running',
            'current_position': 0,
            'total': len(students),
            'completed': 0,
            'failed': 0,
            'start_time': time.time(),
            'elapsed_seconds': 0,
            'log': [],
            'errors': []
        }
        self._should_stop = False
        self._should_pause = False
        
        # Start processing in background
        self.task = asyncio.create_task(self._process_submissions())
        
        logger.info(f"Started submission: {len(students)} students")
        
        return {
            'status': 'started',
            'total': len(students)
        }
    
    async def pause(self) -> Dict:
        """
        Pause submission at current position.
        
        Returns:
            Dictionary with paused status and position
        """
        if self.state['status'] != 'running':
            raise Exception(f"Cannot pause when status is {self.state['status']}")
        
        self._should_pause = True
        self.state['status'] = 'paused'
        
        logger.info(f"Pausing submission at position {self.state['current_position']}")
        
        return {
            'status': 'paused',
            'position': self.state['current_position']
        }
    
    async def resume(self) -> Dict:
        """
        Resume submission from paused position.
        
        Returns:
            Dictionary with resumed status
        """
        if self.state['status'] != 'paused':
            raise Exception(f"Cannot resume when status is {self.state['status']}")
        
        self.state['status'] = 'running'
        self._should_pause = False
        
        # Resume processing
        self.task = asyncio.create_task(self._process_submissions())
        
        logger.info(f"Resuming submission from position {self.state['current_position']}")
        
        return {
            'status': 'running',
            'resumed_from': self.state['current_position']
        }
    
    async def kill(self) -> Dict:
        """
        Stop submission completely and reset state.
        
        Returns:
            Dictionary with killed status and final position
        """
        final_position = self.state['current_position']
        
        self._should_stop = True
        self.state['status'] = 'killed'
        
        # Close automation if running
        if self.automation:
            try:
                await self.automation.stop()
            except:
                pass
            self.automation = None
        
        logger.info(f"Killed submission at position {final_position}")
        
        return {
            'status': 'killed',
            'final_position': final_position
        }
    
    async def _process_submissions(self):
        """
        Internal method to process submissions one by one.
        Handles pause/resume/kill logic.
        """
        try:
            # Initialize Playwright automation if not already started
            if not self.automation:
                self.automation = FormAutomation()
                await self.automation.start()
            
            # Process each student from current position
            while self.state['current_position'] < self.state['total']:
                # Check for pause or kill
                if self._should_pause:
                    logger.info("Pausing execution...")
                    return
                
                if self._should_stop:
                    logger.info("Stopping execution...")
                    return
                
                # Get current student
                student = self.students[self.state['current_position']]
                row_number = student.get('row_number', self.state['current_position'] + 1)
                student_data = student['data']
                
                # Get student name for logging
                student_name = f"{student_data.get('First Name', '')} {student_data.get('Last Name', '')}".strip()
                
                logger.info(f"Processing Row {row_number}: {student_name}")
                
                try:
                    # Fill and submit the form
                    # NOTE: Change submit=True when ready for production
                    
                    result = await self.automation.fill_form(
                        url=self.url,
                        student_data=student_data,
                        submit=False  # Set to True for production (currently testing mode)
                    )
                    
                    if result['success']:
                        # Success
                        self.state['completed'] += 1
                        log_entry = {
                            'row': row_number,
                            'status': 'success',
                            'student': student_name,
                            'timestamp': datetime.now().isoformat()
                        }
                        self.state['log'].append(log_entry)
                        logger.info(f"✓ Row {row_number}: Success - {student_name}")
                    else:
                        # Failed
                        self.state['failed'] += 1
                        error_msg = result.get('message', 'Unknown error')
                        log_entry = {
                            'row': row_number,
                            'status': 'failed',
                            'student': student_name,
                            'error': error_msg,
                            'timestamp': datetime.now().isoformat()
                        }
                        self.state['log'].append(log_entry)
                        self.state['errors'].append(f"Row {row_number}: {error_msg}")
                        logger.error(f"✗ Row {row_number}: Failed - {student_name} - {error_msg}")
                
                except Exception as e:
                    # Exception during submission
                    error_msg = str(e)
                    logger.error(f"✗ Row {row_number}: Exception - {student_name} - {error_msg}")
                    
                    # If browser-related error, try to restart browser
                    if "browser" in error_msg.lower() or "closed" in error_msg.lower() or "disconnected" in error_msg.lower():
                        logger.warning("Browser error detected, attempting restart...")
                        try:
                            await asyncio.wait_for(self.automation.stop(), timeout=3.0)
                        except:
                            pass
                        try:
                            await self.automation.start()
                            logger.info("Browser restarted successfully")
                        except Exception as restart_error:
                            logger.error(f"Failed to restart browser: {restart_error}")
                    
                    self.state['failed'] += 1
                    log_entry = {
                        'row': row_number,
                        'status': 'failed',
                        'student': student_name,
                        'error': error_msg,
                        'timestamp': datetime.now().isoformat()
                    }
                    self.state['log'].append(log_entry)
                    self.state['errors'].append(f"Row {row_number}: {error_msg}")
                
                # Move to next student
                self.state['current_position'] += 1
                
                # Small delay to prevent browser instability
                await asyncio.sleep(0.2)
            
            # All done
            self.state['status'] = 'completed'
            logger.info(f"Submission completed: {self.state['completed']} successful, {self.state['failed']} failed")
            
        except Exception as e:
            logger.error(f"Fatal error in submission processing: {str(e)}")
            self.state['status'] = 'error'
            self.state['errors'].append(f"Fatal error: {str(e)}")
        
        finally:
            # Clean up automation
            if self.automation and self.state['status'] in ['completed', 'error', 'killed']:
                try:
                    await self.automation.stop()
                except:
                    pass
                self.automation = None


# Global instance (singleton pattern for simplicity)
submission_manager = SubmissionManager()

