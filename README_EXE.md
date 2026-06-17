# POS System - Executable Version

## Installation

1. Run `install_pos.bat` to install the application
2. The application will be installed to `C:\POSSystem`
3. A desktop shortcut will be created

## Manual Installation

1. Create a folder `C:\POSSystem`
2. Copy `POSSystem.exe` to this folder
3. Copy the `config`, `assets`, and `static` folders to the same location
4. Run `POSSystem.exe`

## Requirements

- Windows 10 or later
- PostgreSQL database server running
- Database connection configured in `config/database.json`

## Configuration

Edit `config/database.json` to configure your database connection:

```json
{
    "host": "localhost",
    "port": 5432,
    "database": "pos_network",
    "user": "admin",
    "password": "admin"
}
```

## Troubleshooting

- If the application doesn't start, check the database connection
- Make sure PostgreSQL is running
- Verify the database exists and credentials are correct
- Check the logs in the application directory

## Support

For support, contact the system administrator.
