#!/bin/bash

# Start the server in the background
python -m awels_mcp.cli serve > server_output.txt 2>&1 &
SERVER_PID=$!

# Give the server a moment to start
sleep 2

# Run the test script
python -m tests.test_mcp_integration

# Capture the exit code
TEST_EXIT_CODE=$?

# Stop the server
kill $SERVER_PID

# Print the server output
echo "Server output:"
cat server_output.txt

# Clean up
rm server_output.txt

exit $TEST_EXIT_CODE
