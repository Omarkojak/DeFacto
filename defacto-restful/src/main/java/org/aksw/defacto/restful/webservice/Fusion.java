package org.aksw.defacto.restful.webservice;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URL;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import javax.annotation.PostConstruct;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.aksw.defacto.Defacto;
import org.aksw.defacto.evidence.Evidence;
import org.aksw.defacto.model.DefactoModel;
import org.aksw.defacto.restful.core.RestModel;
import org.aksw.defacto.restful.mongo.MongoManager;
import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;
import org.json.JSONArray;
import org.json.JSONObject;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import com.hp.hpl.jena.graph.NodeFactory;
import com.hp.hpl.jena.graph.Triple;
import com.mongodb.DBObject;
import com.mongodb.util.JSON;

@RestController
@RequestMapping("/fusion")
public class Fusion {
  public static Logger LOG = LogManager.getLogger(Fusion.class);

  public static final String collectionTriple = "triple";
  public static final String collectionData = "data";
  public static final String collectionResults = "result";

  protected static final String resultId = "resultId";

  protected MongoManager mongoTriple = null;
  protected MongoManager mongoData = null;
  protected MongoManager mongoResults = null;

  protected RestModel model = null;

  /**
   * Defacto config and example data loading.
   */
  @PostConstruct
  protected void init() {
    model = new RestModel();
    mongoTriple = MongoManager.getMongoManager().setCollection(collectionTriple);
    mongoData = MongoManager.getMongoManager().setCollection(collectionData);
    mongoResults = MongoManager.getMongoManager().setCollection(collectionResults);
  }

  /**
   * method: GET<br>
   * path: id/<id>/input<br>
   *
   * @param id [0-9a-fA-F]{24}
   * @param response
   * @return
   */
  @RequestMapping(value = "/id/{id:^[0-9a-fA-F]{24}$}", produces = "application/json",
      method = RequestMethod.GET)
  @ResponseBody
  public String id(@PathVariable("id") final String id) {
    try {
      final JSONObject triple = new JSONObject(mongoTriple.findDocumentById(id).toString());
      LOG.info(triple.toString(2));
      final Iterator<DBObject> datas = mongoData.find(new JSONObject().put("id", id).toString());
      while (datas.hasNext()) {
        final JSONObject data = new JSONObject(datas.next().toString());
        if (data.has(resultId)) {
          data.put("result",
              new JSONObject(mongoResults.findDocumentById(data.getString(resultId)).toString()));
        }
        if (!triple.has("data")) {
          triple.put("data", new JSONArray());
        }
        triple.getJSONArray("data").put(data);
      }
      LOG.info(triple.toString(2));
      return triple.toString(2);
    } catch (final Exception e) {
      LOG.error(e.getLocalizedMessage(), e);
      return new JSONObject().put("error", e.getLocalizedMessage()).toString(2);
    }
  }

  /**
   * <code>
   http://localhost:4441/fusion/insert?s=http://data.dbpedia.org/resource/Q1000051&p=http://dbpedia.org/ontology/birthPlace&o=http://data.dbpedia.org/resource/Q54156
  </code>
   *
   * method: POST<br>
   * path: insert/<br>
   *
   * @return json object
   */
  @RequestMapping(value = "/insert", method = RequestMethod.GET)
  @ResponseBody
  public ResponseEntity<Object> insert(@RequestParam final String s, @RequestParam final String p,
      @RequestParam final String o, final HttpServletRequest request,
      final HttpServletResponse response) {
    String id = "";
    try {
      new URI(s);
      new URI(p);
      new URI(o);

      final String q = new JSONObject().put("s", s).put("p", p).put("o", o).toString();
      final Iterator<DBObject> iter = mongoTriple.find(q);
      final JSONArray ja = new JSONArray();
      while (iter.hasNext()) {
        ja.put(new JSONObject(iter.next().toString()));
      }

      if (ja.length() > 1) {
        LOG.info("Results found in DB for (" + q + "): " + ja.length());
      }

      // we expect to have just one result for a given s,p,o
      if (ja.length() > 0) {
        id = ja.getJSONObject(0).getJSONObject("_id").getString("$oid").toString();
        triple(id, ja.getJSONObject(0));
        // redirect
        final HttpHeaders httpHeaders = new HttpHeaders();
        URI uri;
        try {
          final URL url = new URL(request.getRequestURL().toString());
          final String redirecturl = url.getProtocol() + "://" + url.getHost()
              + (url.getPort() > -1 ? ":" + url.getPort() : "");
          uri = new URI(redirecturl + "/#/facts/" + id);
          httpHeaders.setLocation(uri);
        } catch (final URISyntaxException e) {
          LOG.error(e.getLocalizedMessage(), e);
        }
        return new ResponseEntity<>(httpHeaders, HttpStatus.SEE_OTHER);
      } else {
        return new ResponseEntity<>("Triple not found in db: " + q, HttpStatus.ACCEPTED);
      }

    } catch (final Exception e) {
      LOG.error(e.getLocalizedMessage(), e);
      try {
        response.sendError(HttpServletResponse.SC_BAD_REQUEST, "Wrong input.");
        response.flushBuffer();
      } catch (final IOException ee) {
        LOG.error(ee.getLocalizedMessage(), ee);
      }
    }
    // TODO
    return new ResponseEntity<>("", HttpStatus.ACCEPTED);
  }

  private void triple(final String id, final JSONObject jo) {
    final Iterator<DBObject> data = mongoData.find(new JSONObject().put("id", id).toString());
    final List<JSONObject> list = new ArrayList<>();
    while (data.hasNext()) {
      list.add(new JSONObject(data.next().toString()));
    }

    final String s = jo.getString("s_dbpedia");
    final String p = jo.getString("p");
    for (final JSONObject o : list) {
      if (!o.has(resultId)) {
        final String rId = defacto(s, p, o.getString("value_dbpedia"));
        if (!rId.isEmpty()) {
          mongoData.coll.update((DBObject) JSON.parse(o.toString()),
              (DBObject) JSON.parse(o.put(resultId, rId).toString()), false, false);
        }
      }
    }
  }

  protected String defacto(final String s, final String p, final String o) {
    // find results in db
    JSONObject find = results(s, p, o);
    if (find == null) {
      // call defacto
      final Triple triple =
          new Triple(NodeFactory.createURI(s), NodeFactory.createURI(p), NodeFactory.createURI(o));

      final DefactoModel defactoModel = model.getModel(triple, "", "");
      final Evidence evidence = Defacto.checkFact(defactoModel, Defacto.TIME_DISTRIBUTION_ONLY.NO);
      final JSONObject jo = model.out(evidence).put("s", s).put("p", p).put("o", o);
      // store results in db
      mongoResults.insert(jo.toString());
      find = results(s, p, o);
    }
    if (find != null) {
      return find.getJSONObject("_id").getString("$oid").toString();
    }
    return "";
  }

  private JSONObject results(final String s, final String p, final String o) {
    final Iterator<DBObject> iter =
        mongoResults.find(new JSONObject().put("s", s).put("p", p).put("o", o).toString());
    while (iter.hasNext()) {
      return new JSONObject(iter.next().toString());
    }
    return null;
  }
}
