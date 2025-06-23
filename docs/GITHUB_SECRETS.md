# GitHub Secrets Configuration for TTSMixmaster

This document outlines the GitHub secrets you need to configure for the automated build and release workflow.

## Required Secrets

### Azure Trusted Signing Secrets

Configure these secrets in your GitHub repository settings under `Settings > Secrets and variables > Actions`:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `AZURE_TENANT_ID` | Your Azure AD tenant ID | `12345678-1234-1234-1234-123456789012` |
| `AZURE_CLIENT_ID` | Service principal client ID | `87654321-4321-4321-4321-210987654321` |
| `AZURE_CLIENT_SECRET` | Service principal client secret | `your-service-principal-secret` |
| `AZURE_TRUSTED_SIGNING_ENDPOINT` | Azure Trusted Signing endpoint URL | `https://eus.codesigning.azure.net/` |
| `AZURE_CODE_SIGNING_ACCOUNT_NAME` | Code signing account name | `your-codesigning-account` |
| `AZURE_CERTIFICATE_PROFILE_NAME` | Certificate profile name | `your-certificate-profile` |

### Repository Secrets

| Secret Name | Description | Auto-Generated |
|-------------|-------------|----------------|
| `GITHUB_TOKEN` | GitHub API token for releases | ✅ Yes (automatic) |

## Setting Up Azure Trusted Signing

### 1. Create an Azure Trusted Signing Account

1. Go to the [Azure Portal](https://portal.azure.com)
2. Search for "Trusted Signing" and create a new account
3. Configure your signing certificate profile

### 2. Create a Service Principal

```bash
# Create service principal
az ad sp create-for-rbac --name "TTSMixmaster-CodeSigning" --role contributor --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group}

# Note down the output:
# - appId (use as AZURE_CLIENT_ID)
# - password (use as AZURE_CLIENT_SECRET)  
# - tenant (use as AZURE_TENANT_ID)
```

### 3. Assign Permissions

Grant the service principal the "Trusted Signing Certificate Profile Signer" role on your code signing account.

### 4. Get Required Values

- **AZURE_TRUSTED_SIGNING_ENDPOINT**: Found in your Trusted Signing account overview
- **AZURE_CODE_SIGNING_ACCOUNT_NAME**: Your Trusted Signing account name
- **AZURE_CERTIFICATE_PROFILE_NAME**: Your certificate profile name

## How to Add Secrets to GitHub

1. Go to your GitHub repository
2. Click `Settings` (repository settings, not account settings)
3. In the left sidebar, click `Secrets and variables > Actions`
4. Click `New repository secret`
5. Add each secret from the table above

## Workflow Triggers

The workflow will trigger on:

1. **Tag Push**: When you push a tag starting with `v` (e.g., `v1.0.0`)
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Manual Trigger**: Via GitHub Actions UI
   - Go to `Actions` tab in your repository
   - Select `Build and Release TTSMixmaster`
   - Click `Run workflow`
   - Enter the version number

## Testing the Workflow

1. **First, test without a release**:
   - Use the manual trigger with a test version like `v0.1.0-test`
   - This will build but not create a public release

2. **Create your first release**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

## Troubleshooting

### Common Issues

1. **Build fails on signing**: Check Azure credentials and permissions
2. **Inno Setup not found**: The workflow automatically installs it
3. **Version detection fails**: Ensure tag format is `vX.Y.Z`

### Debug Tips

- Check the Actions tab for detailed logs
- Verify all secrets are set correctly
- Test Azure signing separately if needed

## Security Notes

- Never commit secrets to your repository
- Use environment-specific secrets for different deployment targets
- Regularly rotate service principal credentials
- Monitor Azure billing for code signing usage
