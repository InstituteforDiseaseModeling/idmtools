

import React from 'react';
import IconButton from '@material-ui/core/IconButton';
import SnackbarContent from '@material-ui/core/SnackbarContent';
import { green } from '@material-ui/core/colors';
import { withStyles } from '@material-ui/core/styles';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import ErrorIcon from '@material-ui/icons/Error';
import InfoIcon from '@material-ui/icons/Info';
import CloseIcon from '@material-ui/icons/Close';
import WarningIcon from '@material-ui/icons/Warning';
import clsx from 'clsx';


const variantIcon = {
    success: CheckCircleIcon,
    warning: WarningIcon,
    error: ErrorIcon,
    info: InfoIcon,
};

const styles = theme => ({
    success: {
      backgroundColor: green[600],
    },
    error: {
      backgroundColor: theme.palette.error.main,
    },
    info: {
      backgroundColor: theme.palette.info.main,
    },
    warning: {
      backgroundColor: theme.palette.info.main, 
    },
    icon: {
      fontSize: 20,
    },
    iconVariant: {
      opacity: 0.9,
      marginRight: 5
    },
    message: {
      display: 'flex',
      alignItems: 'center',
    },

  });

function SnackbarContentWrapper(props) {
    const {classes}  = props;
    const { className, message, onClose, variant, ...other } = props;
    const Icon = variantIcon[variant];
  
    return (
      <SnackbarContent
        className={clsx(classes[variant], className, classes.root)}
        aria-describedby="client-snackbar"
        message={
          <span id="client-snackbar" className={classes.message}>
            <Icon className={clsx(classes.icon, classes.iconVariant)} />
            {message}
          </span>
        }
        action={[
          <IconButton key="close" aria-label="Close" color="inherit" onClick={onClose}>
            <CloseIcon className={classes.icon} />
          </IconButton>,
        ]}        
        {...other}
      />
    );
  }


  export default withStyles(styles,{ withTheme: true })(SnackbarContentWrapper);
