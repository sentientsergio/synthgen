# API Key Management in SynthGen

This document outlines the best practices for managing API keys in the SynthGen project.

## API Key Setup

### Option 1: Using a .env File (Recommended for Development)

1. Create a `.env` file in the project root directory
2. Add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```
3. Make sure this file is not committed to version control (it's already in `.gitignore`)

### Option 2: Environment Variables

Set the environment variable directly in your shell:

**Linux/macOS:**

```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

**Windows:**

```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

## Best Practices for API Key Security

1. **Never hardcode API keys** in source code
2. **Never commit API keys** to version control
3. **Rotate keys periodically** for enhanced security
4. **Use separate API keys** for development and production
5. **Set usage limits** on your OpenAI account to prevent unexpected charges
6. **Monitor API usage** to detect unusual activity

## Key Validation

SynthGen validates API keys to ensure they have the correct format:

- OpenAI API keys should start with `sk-` followed by alphanumeric characters
- The system will detect if you accidentally use an API key from another provider (like Anthropic/Claude)

## Testing API Connectivity

You can verify your API key and connectivity by running:

```bash
python tests/integration/test_openai_connectivity.py
```

This test will validate your API key format and make a minimal test call to ensure everything is working correctly.

## Troubleshooting

### Environment Variables vs .env File

If you're using a `.env` file but the connectivity test still fails:

1. **Check for conflicting environment variables**: Environment variables take precedence over values in the `.env` file. If you have an `OPENAI_API_KEY` environment variable already set, it will be used instead of the one in your `.env` file.

   To check for existing environment variables:

   ```bash
   # Linux/macOS
   echo $OPENAI_API_KEY

   # Windows
   echo %OPENAI_API_KEY%
   ```

2. **Clear existing environment variables**:

   ```bash
   # Linux/macOS
   unset OPENAI_API_KEY

   # Windows
   set OPENAI_API_KEY=
   ```

### Invalid API Key Format

If you see an error about invalid API key format:

1. **Verify you're using an OpenAI key**: OpenAI API keys start with `sk-` followed by alphanumeric characters
2. **Check for whitespace**: Ensure there are no extra spaces or newlines in your API key
3. **Check for quoting**: Don't include quotes around your API key in the `.env` file

## API Keys in CI/CD

For CI/CD pipelines, store API keys as secure environment variables in your CI system:

- GitHub Actions: Use repository secrets
- Jenkins: Use credentials binding
- GitLab CI: Use CI/CD variables

## Production Deployments

For production deployments, consider using a dedicated secrets management solution:

- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Google Secret Manager
