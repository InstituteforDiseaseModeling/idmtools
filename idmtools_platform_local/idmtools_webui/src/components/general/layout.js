import React from "react";

import { withStyles } from '@material-ui/core/styles';
import { connect } from "react-redux";
import { AppBar, Toolbar, Typography, IconButton, List, ListItemIcon, ListItem, ListItemText, Snackbar } from "@material-ui/core";
import MenuIcon from "@material-ui/icons/Menu";
import MailIcon from '@material-ui/icons/Mail';
import InboxIcon from '@material-ui/icons/MoveToInbox';

import Divider from '@material-ui/core/Divider';
import idmlogo from '../../images/idmlogo55.png';
import Dashboard from "../views/dashboardView";

import {EXPERIMENT_VIEW, SIMULATION_VIEW} from "../../redux/actionTypes"

import ExperimentView from "../views/experimentView"
import SimulationView from "../views/simulationView"
import 'react-splitter-layout/lib/index.css';
import SnackbarContentWrapper from "./SnackBarContentWrapper";
import {showStop} from "../../redux/action/messaging";


const drawerWidth = 192;


const styles = theme => ({

  root: {    
    display: 'flex',
    height:'100%'
  },
  logo: {
    display:'flex',
    padding: '10px 20px'
  },
  idmlogo: { 
    //position: 'absolute',
    //clip: 'rect(0px, 45px, 100px,0px)',
    marginTop:5,
    width: 30,
    height: 30
  },

  heading:{
    color:'#a1a1a1',
    width:'100%',
    padding: '5px 8px'
  },

  content: {
    flexGrow: 1,
    backgroundColor: '#585454',
    marginLeft:`${drawerWidth}px`,
    position:'relative',
    height: `calc(100% - 64px)`
    //padding: theme.spacing(3),
  },
  appBar: {
    marginLeft: drawerWidth,
    [theme.breakpoints.up('sm')]: {
      width: `calc(100% - ${drawerWidth}px)`,
    },
  },
  toolbar: theme.mixins.toolbar,
  nav: {
    position:'fixed'
  },
  snackbar: {
    zIndex:10001,
    top:4
  },
  title : {
    paddingLeft: theme.spacing(1)
  }


});


class Layout extends React.Component {



  navigate(target) {
    return ()=> {
      
      window.location.href = "/" + target;
    }
  }

  handleSnackBarClose = (event) => {
      
    this.props.dispatch(showStop());
  };


  render() {
    const { classes, simulations, selectedView, variant } = this.props; // eslint-disable-line no-unused-vars


    
    let view = <Dashboard/>;

    if (selectedView && selectedView.selectedView === EXPERIMENT_VIEW) {
      view = <ExperimentView/>
    } else if (selectedView && selectedView.selectedView === SIMULATION_VIEW) {
      view = <SimulationView/>
    }



    let title = selectedView ? selectedView.selectedTitle : 'Dashboard';

    return (
      <div className={classes.root}>

        <AppBar position="fixed" className={classes.appBar}>
          <Toolbar>
            <IconButton edge="start" className={classes.menuButton} color="inherit" aria-label="menu">
              <MenuIcon />              
            </IconButton>
            <Typography variant="h5" className={classes.title}>{title}</Typography>
            
          </Toolbar>

        </AppBar>
        <nav className={classes.nav}>
          <div>
            <div className={classes.toolbar}>

                <div className={classes.logo}>
                  <img src={idmlogo} title="Institute for Disease Modeling" alt={"IDMlogo"} className={classes.idmlogo}></img>
                  <Typography variant="h5" className={classes.heading}>IDM Tools</Typography>
                </div>
              
            </div>
            <Divider />
            <List>
              {['Dashboard','Simulation', 'Experiment'].map((text, index) => (
                <ListItem button key={text} onClick={this.navigate(text)} >
                  <ListItemIcon>{index % 2 === 0 ? <InboxIcon /> : <MailIcon />}</ListItemIcon>
                  <ListItemText primary={text} />
                </ListItem>
              ))}
            </List>
          </div>
        </nav>

        <main className={classes.content}>
          <div className={classes.toolbar} />
          {view}
          <Snackbar
                    
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'center',
            }}
            open={this.props.showMsg}
            autoHideDuration={variant === "error" ? null : 6000}
              onClose={this.handleSnackBarClose}
            className={classes.snackbar}
          >
            <SnackbarContentWrapper
                onClose={this.handleSnackBarClose}
              variant={this.props.variant}
              message={this.props.infoMsg}
            />
          </Snackbar>
        </main>

      </div>

    )

  }
}

function mapStateToProps(state) {

  const {  changeView, showMsg } = state;

  return ({
    simulations: state.simulations,
    selectedView: changeView,
    showMsg: showMsg.open,
    infoMsg: showMsg.msg,
    variant: showMsg.variant

  })

}

export default connect(mapStateToProps)(withStyles(styles, { withTheme: true })(Layout));
