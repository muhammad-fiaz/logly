# Security Policy

## Supported Versions

We take security seriously and actively maintain security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.3+  | :white_check_mark: |
| < 0.1.3 | :x:                |

> **Note**: Versions below 0.1.3 lack many features that have been updated, improved, or removed. We strongly recommend always using the latest version for the best experience and security.

## Reporting a Vulnerability

If you discover a security vulnerability in Logly, please help us by reporting it responsibly.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by emailing:
- **Email**: contact@muhammadfiaz.com
- **Subject**: [SECURITY] Logly Vulnerability Report

### What to Include

When reporting a security vulnerability, please include:

1. **Description**: A clear description of the vulnerability
2. **Impact**: What an attacker could achieve by exploiting this vulnerability
3. **Steps to Reproduce**: Detailed steps to reproduce the issue
4. **Affected Versions**: Which versions of Logly are affected
5. **Mitigation**: Any suggested fixes or workarounds (optional)

### Our Commitment

- We will acknowledge receipt of your report within 48 hours
- We will provide a more detailed response within 7 days indicating our next steps
- We will keep you informed about our progress throughout the process
- We will credit you (if desired) once the vulnerability is fixed

### Disclosure Policy

- Once we have confirmed and fixed a vulnerability, we will:
  - Release a security advisory on GitHub
  - Update the changelog with details about the fix
  - Credit the reporter (with permission)

## Security Best Practices

When using Logly in production:

1. **Keep Dependencies Updated**: Regularly update Logly and its dependencies
2. **Log Sanitization**: Be cautious with sensitive data in log messages
3. **Access Control**: Limit access to log files and configuration
4. **Monitor Logs**: Implement monitoring for suspicious logging activity
5. **Environment Variables**: Use environment variables for sensitive configuration

## Contact

For security-related questions or concerns, please use the contact information above rather than creating public issues.