# Usage Examples

## ChatGPT Conversation Examples

### Starting a New Session

**You**: "Create a new Claude-Code session called 'web-app' in my ~/projects/my-app directory"

**ChatGPT**: I'll create a new Claude-Code session for you.

*[Uses create_session tool]*

Session "web-app_a1b2c3d4" created successfully in ~/projects/my-app!

### Sending Commands

**You**: "Tell the web-app session to create a new React component called UserProfile"

**ChatGPT**: I'll send that request to your Claude-Code session.

*[Uses send_message tool]*

Message sent to session web-app_a1b2c3d4: "Create a new React component called UserProfile"

Claude-Code is now working on creating the UserProfile component.

### Checking Session Status

**You**: "What's the status of all my Claude-Code sessions?"

**ChatGPT**: Let me check your active sessions.

*[Uses list_sessions tool]*

You have 2 active Claude-Code sessions:

1. **web-app_a1b2c3d4**
   - Status: Active
   - Working directory: ~/projects/my-app
   - Created: 10 minutes ago
   - Last activity: 2 minutes ago

2. **api-server_b2c3d4e5**
   - Status: Active
   - Working directory: ~/projects/backend
   - Created: 1 hour ago
   - Last activity: 5 minutes ago

### Getting Logs

**You**: "Show me the last 20 lines from the web-app session"

**ChatGPT**: Here are the recent logs from your web-app session:

*[Uses get_logs tool]*

```
[14:23:15] USER: Create a new React component called UserProfile
[14:23:16] I'll help you create a new React component called UserProfile...
[14:23:18] Creating src/components/UserProfile.jsx
[14:23:20] Adding TypeScript types for UserProfile props
[14:23:22] Component created successfully with:
[14:23:22] - Profile display with avatar and name
[14:23:22] - Editable user information form
[14:23:22] - Responsive design with Tailwind CSS
[14:23:23] Would you like me to create tests for this component?
```

### Handling Stuck Commands

**You**: "Check if any of my sessions are waiting for input"

**ChatGPT**: Let me check for any interactive prompts.

*[Uses check_prompts tool]*

I found 1 session waiting for input:

**Session web-app_a1b2c3d4** is asking:
"Do you want me to install the additional dependency 'react-hook-form'? [y/n]"

**You**: "Tell it yes"

**ChatGPT**: I'll respond "y" to the prompt.

*[Uses respond_to_prompt tool]*

Response sent! The session will now proceed with installing react-hook-form.

### Polishing Messages

**You**: "I want to tell the web-app session to add authentication, but make it sound professional"

**ChatGPT**: I'll help you craft a professional request:

"Please implement a comprehensive authentication system including:
- User registration and login components
- JWT token management
- Protected route guards
- Password reset functionality
- Integration with the existing UserProfile component

Please follow security best practices and include proper error handling."

Should I send this message to the web-app session?

**You**: "Perfect, send it"

**ChatGPT**: *[Uses send_message tool]*

Professional authentication request sent to web-app_a1b2c3d4!

## Common Workflows

### 1. Mobile Development Check-in

While away from your Mac:

1. "List my Claude-Code sessions"
2. "Show me logs from my mobile-app session"
3. "Tell the mobile-app session to run the tests and commit if they pass"
4. "Check if any sessions need my input"

### 2. Multi-Project Management

Managing multiple projects:

1. "Create sessions for each of my projects: web-frontend, api-backend, mobile-app"
2. "Tell the web-frontend session to update the user dashboard"
3. "Tell the api-backend session to add rate limiting to the auth endpoints"
4. "Show me the status of all three sessions"

### 3. Debugging and Monitoring

When things go wrong:

1. "Check if any sessions are stuck waiting for input"
2. "Show me the last 100 lines from the problematic session"
3. "Tell that session to cancel the current operation and try a different approach"
4. "If needed, terminate the stuck session and create a new one"

## MCP Tools Reference

| Tool | Purpose | Example |
|------|---------|---------|
| `list_sessions` | Get all active sessions | "What sessions are running?" |
| `create_session` | Start new Claude-Code | "Create a session in my project folder" |
| `send_message` | Send command to session | "Tell it to add unit tests" |
| `get_logs` | Retrieve session output | "Show me recent logs" |
| `get_session_status` | Check session details | "What's the status of session X?" |
| `terminate_session` | Stop a session | "Terminate the stuck session" |
| `check_prompts` | Find pending prompts | "Any sessions waiting for input?" |
| `respond_to_prompt` | Answer prompts | "Tell it 'yes'" |

## Tips for Effective Usage

1. **Be Specific**: Include session names when you have multiple active
2. **Check Regularly**: Monitor sessions for stuck prompts
3. **Use Descriptive Names**: Name sessions by project or task
4. **Monitor Resources**: Don't leave too many sessions running
5. **Backup Important Work**: Regularly commit code from active sessions