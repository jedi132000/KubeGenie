# Changelog

All notable changes to KubeGenie will be documented in this file.

## [1.1.0] - 2025-10-06

### Added
- **OpenAI Integration**: Real conversational AI powered by GPT-3.5-turbo
- **Enhanced Authentication**: Consistent token-based authentication across all endpoints
- **Test UI Interface**: Comprehensive button testing interface at port 7880
- **Environment Configuration**: Proper .env setup with OpenAI API key support
- **Gradio UI Improvements**: Upgraded to Gradio 4.20.0 for better compatibility

### Changed
- **Authentication System**: Unified simple token system across auth and chat endpoints
- **Chat Endpoint**: Updated to use Bearer token authentication instead of JWT
- **Setup Process**: Improved documentation with absolute paths and virtual environment usage
- **Error Handling**: Better error reporting in chat and authentication flows

### Fixed
- **Authentication Mismatch**: Fixed inconsistency between login tokens and chat endpoint validation
- **Gradio Compatibility**: Resolved Gradio version compatibility issues
- **Token Validation**: Fixed "Could not validate credentials" error in chat endpoint
- **Virtual Environment**: Ensured all services run with proper virtual environment activation

### Security
- **Environment Variables**: Added .env.example template without sensitive information
- **Token Security**: Implemented proper Bearer token format for API authentication
- **Secrets Management**: Ensured sensitive API keys are excluded from version control

### Technical Details
- Backend: FastAPI with OpenAI client v1.3.0+
- Frontend: Gradio 4.20.0 with enhanced UI components
- Authentication: Simple token system with Bearer authorization headers
- Testing: Comprehensive test interface for all endpoints

## [1.0.0] - 2025-10-01

### Added
- Initial release of KubeGenie
- FastAPI backend with Kubernetes integration
- Basic Gradio web interface
- CLI tool for terminal operations
- Docker containerization support
- Basic authentication system