// src/component/content.jsx

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Box, Paper, Typography, Button, Avatar } from '@mui/material';
import { ReactMediaRecorder } from 'react-media-recorder';
import MicIcon from '@mui/icons-material/Mic';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { keyframes } from '@emotion/react';

// Blink animation for the mic button when recording
const blink = keyframes`
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
`;

// List of questions to be asked
const questions = [
  "What's your name & Age?",
  "What's your education Level and Background?",
  "At which level are you Teaching (e.g., 7th grade, graduate program)?",
  "In which field do you want to learn?",
  "Do you have any prior understanding about the topic or field you wish to learn?",
  "Any specific topic you want to learn?"
];

const Content = () => {
  const [hasStarted, setHasStarted] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [recordedAnswers, setRecordedAnswers] = useState(Array(questions.length).fill(null));
  const [tempRecording, setTempRecording] = useState(null);

  // Speak the question using the SpeechSynthesis API whenever it changes
  useEffect(() => {
    if (hasStarted) {
      const utterance = new SpeechSynthesisUtterance(questions[currentQuestion]);
      window.speechSynthesis.speak(utterance);
    }
  }, [currentQuestion, hasStarted]);

  // Process the recorded audio by sending it to your backend for transcription
  const processRecording = async (blob, mediaBlobUrl) => {
    const formData = new FormData();
    formData.append('file', blob, 'recording.wav');
    try {
      const response = await axios.post('http://localhost:8000/api/transcribe', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      const transcription = response.data.transcription;
      setTempRecording({ blob, mediaBlobUrl, transcription });
    } catch (error) {
      console.error("Error transcribing audio:", error);
    }
  };

  // Advance to the next question
  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setTempRecording(null);
    } else {
      console.log("All questions answered", recordedAnswers);
      alert("Thank you for your responses!");
    }
  };

  // Initial start screen with welcome message and a big circular start button
  if (!hasStarted) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, textAlign: 'center' }}>
        <Typography
          variant="h4"
          sx={{
            mb: 4,
            fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' }
          }}
        >
          Hello, welcome to our AI model! <br /> Press the Start button to begin learning.
        </Typography>
        <Button 
          variant="contained" 
          onClick={() => setHasStarted(true)}
          sx={{
            width: { xs: 100, sm: 120, md: 150 },
            height: { xs: 100, sm: 120, md: 150 },
            borderRadius: '50%',
            backgroundColor: '#3b82f6',
            color: 'white',
            fontSize: { xs: '2rem', sm: '2.5rem', md: '3rem' },
            transition: 'transform 0.3s, background-color 0.3s',
            '&:hover': {
              transform: 'scale(1.05)',
              backgroundColor: '#2563eb'
            }
          }}
        >
          <PlayArrowIcon fontSize="inherit" />
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Paper sx={{ p: 3, backgroundColor: '#1f2937', color: '#f9fafb' }} elevation={3}>
        <Box display="flex" flexDirection="column" alignItems="center" mb={2}>
          <Typography variant="subtitle1" sx={{ color: '#9ca3af' }}>
            Your AI Assistant
          </Typography>
        </Box>
        <Typography
          variant="h4"
          align="center"
          gutterBottom
          sx={{
            fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' }
          }}
        >
          {questions[currentQuestion]}
        </Typography>
        <Box display="flex" flexDirection="column" alignItems="center" mt={4}>
          <ReactMediaRecorder
            audio
            onStop={(mediaBlobUrl) => {
              fetch(mediaBlobUrl)
                .then((res) => res.blob())
                .then((blob) => processRecording(blob, mediaBlobUrl));
            }}
            render={({ status, startRecording, stopRecording, mediaBlobUrl, clearBlobUrl }) => (
              <Box textAlign="center">
                <Typography
                  variant="subtitle1"
                  gutterBottom
                  sx={{ fontSize: { xs: '0.8rem', sm: '1rem', md: '1.2rem' } }}
                >
                  Status: {status}
                </Typography>

                {/* Big Circle Mic Button (start) */}
                {(!tempRecording && !recordedAnswers[currentQuestion] && status !== 'recording') && (
                  <Button 
                    onClick={startRecording}
                    sx={{
                      width: { xs: 80, sm: 100, md: 120 },
                      height: { xs: 80, sm: 100, md: 120 },
                      borderRadius: '50%',
                      backgroundColor: '#3b82f6',
                      color: 'white',
                      fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' },
                      minWidth: 0,
                      p: 0,
                      transition: 'background-color 0.3s, transform 0.3s',
                      '&:hover': {
                        backgroundColor: '#2563eb',
                        transform: 'scale(1.05)'
                      }
                    }}
                  >
                    <MicIcon fontSize="inherit" />
                  </Button>
                )}

                {/* Blinking Mic Button When Recording */}
                {status === 'recording' && (
                  <Button 
                    onClick={stopRecording}
                    sx={{
                      width: { xs: 80, sm: 100, md: 120 },
                      height: { xs: 80, sm: 100, md: 120 },
                      borderRadius: '50%',
                      backgroundColor: '#ef4444',
                      color: 'white',
                      fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' },
                      minWidth: 0,
                      p: 0,
                      animation: `${blink} 1s infinite`,
                      transition: 'background-color 0.3s, transform 0.3s',
                      '&:hover': {
                        backgroundColor: '#dc2626'
                      }
                    }}
                  >
                    <MicIcon fontSize="inherit" />
                  </Button>
                )}

                {/* Confirmation UI after recording stops */}
                {tempRecording && (
                  <Box mt={2}>
                    <audio src={tempRecording.mediaBlobUrl} controls />
                    <Typography variant="body2" sx={{ mt: 1, fontSize: { xs: '0.8rem', sm: '1rem', md: '1.2rem' } }}>
                      I heard: "{tempRecording.transcription}"
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 1, fontSize: { xs: '0.8rem', sm: '1rem', md: '1.2rem' } }}>
                      Is this correct?
                    </Typography>
                    <Box mt={1}>
                      <Button
                        variant="contained"
                        onClick={() => {
                          setRecordedAnswers(prev => {
                            const newArr = [...prev];
                            newArr[currentQuestion] = tempRecording;
                            return newArr;
                          });
                          setTempRecording(null);
                        }}
                        sx={{
                          backgroundColor: '#10b981',
                          color: 'white',
                          transition: 'background-color 0.3s',
                          '&:hover': {
                            backgroundColor: '#059669'
                          },
                          fontSize: { xs: '0.8rem', sm: '0.9rem', md: '1rem' }
                        }}
                      >
                        Yes, it's correct
                      </Button>
                      <Button
                        variant="outlined"
                        onClick={() => {
                          setTempRecording(null);
                          if (clearBlobUrl) clearBlobUrl();
                        }}
                        sx={{
                          borderColor: '#64748b',
                          color: '#64748b',
                          ml: 2,
                          transition: 'border-color 0.3s, color 0.3s',
                          '&:hover': {
                            borderColor: '#475569',
                            color: '#475569'
                          },
                          fontSize: { xs: '0.8rem', sm: '0.9rem', md: '1rem' }
                        }}
                      >
                        Re-record
                      </Button>
                    </Box>
                  </Box>
                )}

                {/* Confirmed answer UI with Next button */}
                {recordedAnswers[currentQuestion] && !tempRecording && (
                  <Box mt={2}>
                    <audio
                      src={URL.createObjectURL(recordedAnswers[currentQuestion].blob)}
                      controls
                    />
                    <Typography variant="body2" sx={{ mt: 1, fontSize: { xs: '0.8rem', sm: '1rem', md: '1.2rem' } }}>
                      Confirmed: "{recordedAnswers[currentQuestion].transcription}"
                    </Typography>
                    <Button 
                      variant="outlined" 
                      onClick={handleNextQuestion}
                      sx={{
                        mt: 2,
                        borderColor: '#3b82f6',
                        color: '#3b82f6',
                        transition: 'border-color 0.3s, color 0.3s',
                        '&:hover': {
                          borderColor: '#2563eb',
                          color: '#2563eb'
                        },
                        fontSize: { xs: '0.8rem', sm: '0.9rem', md: '1rem' }
                      }}
                    >
                      Next Question
                    </Button>
                  </Box>
                )}
              </Box>
            )}
          />
        </Box>
      </Paper>
    </Container>
  );
};

export default Content;
