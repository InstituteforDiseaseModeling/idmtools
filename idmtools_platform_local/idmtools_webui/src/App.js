import React from 'react';
import logo from './logo.svg';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import Hidden from '@material-ui/core/Hidden';
import CssBaseline from '@material-ui/core/CssBaseline';


import './App.css';
import Layout from "./components/general/layout"
import configureStore from "./redux/store";
import { Provider } from "react-redux";
import blue from '@material-ui/core/colors/blue';
import RouterContainer from './components/general/routerContainer';

const store = configureStore();

const theme = createMuiTheme({

  palette: {
    primary: {
      main: '#2a2a2a',
      light: '#00bcd4'
    },
    type: 'dark',
    background: {
      default: "#4c4c4c"
    },
    error: {
      main: '#ef5350'
    },
    warning: {
      main: '#ffc107',  //yellow
    },
    info: {
      main: '#66bb6a'  //green
    }
  },
  app: {
    //height:'100%'
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
      '"Apple Color Emoji"',
      '"Segoe UI Emoji"',
      '"Segoe UI Symbol"',
    ].join(','),
    fontColor:'#6f9a37',
    color:'#6f9a37'
  }

})


function App() {
  return (
    <Provider store={store}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        <RouterContainer>
          <div style={{height:'100%'}}>
            <Layout />
          </div>
        </RouterContainer>
      </MuiThemeProvider>
    </Provider>
  );
}

export default App;
